"""Full-set production, global audit and accepted-output protection; synthetic data."""
from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from scripts.zhishu import module_package as m
from scripts.zhishu import module_release as release
from tests import test_zhishu_module_package as fixture


class ModuleReleaseTests(unittest.TestCase):
    setUp = fixture.ModulePackageTests.setUp
    tearDown = fixture.ModulePackageTests.tearDown
    write_full = fixture.ModulePackageTests.write_full

    def expand(self):
        roots = {r['id'] for r in self.data['knowledgeNodes']}
        for i, (slug, registration) in enumerate(m.MODULES.items()):
            _, _, root, title = registration
            if root in roots:
                continue
            uid = f'Z{i:03}'
            self.data['knowledgeNodes'].extend([
                {'id': root, 'title': title, 'type': 'chapter', 'parentId': m.ROOT, 'sortOrder': 200 + i},
                {'id': uid, 'title': '原数学 α≤β', 'type': 'knowledge', 'parentId': root, 'sortOrder': 10},
            ])
            self.data['searchDocuments'].append({'knowledgeNodeId': uid, 'title': '原数学 α≤β',
                                                'summary': '中文摘要 ∀x∈ℝ', 'breadcrumb': [title]})
        # A real Section under prerequisites must remain a Section with its parent chain.
        self.data['knowledgeNodes'].append({'id': 'struct:前置知识/原分支', 'title': '原分支',
            'type': 'section', 'parentId': 'struct:前置知识', 'sortOrder': 10})
        next(r for r in self.data['knowledgeNodes'] if r.get('parentId') == 'struct:前置知识'
             and r['type'] == 'knowledge')['parentId'] = 'struct:前置知识/原分支'
        self.write_full()

    def produce(self, output=None):
        return release.produce_release(self.source, self.root / 'staging', output)

    def test_all_chapters_discovered_and_stable_unique_identity(self):
        self.expand()
        self.assertEqual(set(m.discover_modules(self.data)), set(m.MODULES))
        self.assertEqual(len(m.MODULES), 14)
        self.assertEqual(m.MODULES['sets'][:2], ('zhishu.math.set', 'math.set'))
        self.assertEqual(m.MODULES['analytic-geometry'][:2],
                         ('zhishu.math.analytic-geometry', 'math.analytic-geometry'))

    def test_all_coverage_media_relations_index_and_determinism(self):
        self.expand()
        before = release.fingerprint(self.source)
        published = self.root / 'published'
        m.slice_modules(self.source, published, ['sets', 'analytic-geometry'])
        result = self.produce(published)
        audit = release.validate_index(self.source, published)
        self.assertTrue(result['byteIdentical'])
        self.assertEqual(audit['moduleCount'], 14)
        self.assertEqual(audit['knowledgeCount'], len(self.data['searchDocuments']))
        self.assertEqual(audit['canonicalRelations'], 3)
        self.assertEqual(audit['internalRelationRecords'], 1)
        self.assertEqual(audit['externalRelationRecords'], 4)
        self.assertEqual(audit['duplicateEndpointDeclarations'], 2)
        self.assertEqual(audit['sharedCategories'], {m.ROOT: 14})
        self.assertEqual(audit['physicalMediaFiles'], 8)
        self.assertEqual(before, release.fingerprint(self.source))
        rows = result['index']['modules']
        self.assertEqual([r['packageId'] for r in rows], sorted(r['packageId'] for r in rows))
        self.assertEqual(release.fingerprint(self.root / 'staging/round-1'),
                         release.fingerprint(self.root / 'staging/round-2'))
        for slug in m.MODULES:
            self.assertEqual(m.validate_module(published / (slug + '.zip'), self.source), ())

    def test_prerequisite_section_and_chinese_search_preserved(self):
        self.expand()
        projected = m.select(self.data, 'prerequisites')
        self.assertIn({'id': 'struct:前置知识/原分支', 'title': '原分支', 'type': 'section',
                      'parentId': 'struct:前置知识', 'sortOrder': 10}, projected['knowledgeNodes'])
        self.assertEqual(projected['searchDocuments'][0]['summary'], '中文摘要 ∀x∈ℝ')

    def test_unknown_chapter_fails_closed(self):
        self.data['knowledgeNodes'][1]['id'] = 'struct:未知'
        self.data['knowledgeNodes'][4]['parentId'] = 'struct:未知'
        with self.assertRaisesRegex(m.ModuleError, 'unregistered source chapter'):
            m.discover_modules(self.data)

    def test_changed_chapter_title_fails_closed(self):
        self.data['knowledgeNodes'][1]['title'] = '更名'
        with self.assertRaisesRegex(m.ModuleError, 'mismatch'):
            m.discover_modules(self.data)

    def test_empty_chapter_not_invented(self):
        self.data['knowledgeNodes'] = [r for r in self.data['knowledgeNodes'] if r['id'] != 'S001']
        with self.assertRaisesRegex(m.ModuleError, 'empty source chapter'):
            m.discover_modules(self.data)

    def test_duplicate_identity_mapping_rejected(self):
        with patch.dict(m.MODULES, {'duplicate': m.MODULES['sets']}):
            with self.assertRaisesRegex(m.ModuleError, 'duplicate registered'):
                m.discover_modules(self.data)

    def test_wrong_module_count_keeps_output(self):
        before = release.fingerprint(self.output)
        with self.assertRaisesRegex(m.ModuleError, 'expected 14 real modules, found 3'):
            self.produce(self.output)
        self.assertEqual(before, release.fingerprint(self.output))

    def test_failed_later_module_preserves_accepted_pilots(self):
        self.expand()
        before = release.fingerprint(self.output)
        original = m.write_zip
        def fail(root, destination):
            if root.name == 'logic':
                raise OSError('injected full-set failure')
            original(root, destination)
        with patch.object(m, 'write_zip', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'injected'):
                self.produce(self.output)
        self.assertEqual(before, release.fingerprint(self.output))
        self.assertFalse((self.output / 'release-index.json').exists())

    def test_changed_accepted_pilot_blocks_promotion_and_keeps_staging(self):
        self.expand()
        next(r for r in self.data['knowledgeNodes'] if r['id'] == 'S001')['title'] += ' updated'
        self.write_full()
        before = release.fingerprint(self.output)
        with self.assertRaisesRegex(m.ModuleError, 'EXISTING_OUTPUT_CHANGED'):
            self.produce(self.output)
        self.assertEqual(before, release.fingerprint(self.output))
        self.assertTrue((self.root / 'staging/round-1/sets.zip').is_file())

    def test_unrelated_official_file_is_preserved(self):
        self.expand()
        (self.output / 'keep.txt').write_text('keep')
        before = release.fingerprint(self.output)
        with self.assertRaisesRegex(m.ModuleError, 'EXISTING_OUTPUT_CHANGED'):
            self.produce(self.output)
        self.assertEqual(before, release.fingerprint(self.output))

    def test_missing_zip_fails_global_audit(self):
        self.expand()
        self.produce()
        packages = self.root / 'staging/round-1'
        (packages / 'logic.zip').unlink()
        with self.assertRaisesRegex(m.ModuleError, 'ZIP set mismatch'):
            release.audit_modules(self.source, packages)

    def test_index_tampered_size_hash_or_identity_rejected(self):
        self.expand()
        self.produce()
        packages = self.root / 'staging/round-1'
        original = m.read_json(packages / 'release-index.json')
        for field, value in [('bytes', 1), ('sha256', '0' * 64), ('packageId', 'other.package')]:
            altered = copy.deepcopy(original)
            altered['modules'][0][field] = value
            m.write_json(packages / 'release-index.json', altered)
            with self.assertRaisesRegex(m.ModuleError, 'release index mismatch'):
                release.validate_index(self.source, packages)

    def test_source_change_before_promotion_is_rejected(self):
        self.expand()
        self.produce()
        frozen = release.fingerprint(self.source)
        frozen['manifest.json'] = 'changed'
        with self.assertRaisesRegex(m.ModuleError, 'frozen source changed'):
            release.promote_release(self.source, self.root / 'staging/round-1', self.output, frozen)

    def test_existing_staging_and_source_overlap_refused(self):
        for staging in (self.source, self.source / 'child', self.root):
            with self.assertRaises(m.ModuleError):
                release.produce_release(self.source, staging)

    def test_transient_windows_rename_retried_without_changing_output(self):
        before = release.fingerprint(self.output)
        original = m.os.replace
        calls = 0
        def transient(source, destination):
            nonlocal calls
            calls += 1
            if calls == 1:
                error = OSError('transient Windows directory handle')
                error.winerror = 5
                raise error
            return original(source, destination)
        with patch.object(m.os, 'replace', side_effect=transient), patch.object(m.time, 'sleep'):
            m.slice_modules(self.source, self.output, ['sets'])
        self.assertGreater(calls, 1)
        self.assertEqual(before, release.fingerprint(self.output))

    def test_unreadable_output_is_not_treated_as_empty(self):
        with patch.object(m.os, 'scandir', side_effect=PermissionError('unreadable output')):
            with self.assertRaisesRegex(PermissionError, 'unreadable output'):
                m.inventory(self.output)


if __name__ == '__main__':
    unittest.main()
