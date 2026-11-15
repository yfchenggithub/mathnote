"""Classification/export checks use real Full serialization and module ZIPs."""
import copy
import json
from pathlib import Path
import unittest
import zipfile

from scripts.check_free_knowledge_selection import SelectionError, validate_nodes, validate_sources, validate_exports
from scripts.zhishu import content_package as full, module_package as module
from scripts.zhishu.runtime_mapping import map_runtime
from scripts.zhishu.source_discovery import MODULE_NAMES, scan_repository
from tests.test_zhishu_content_package import meta_record


class FreeSelectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = module.temporary_directory()
        self.root = self.tmp.__enter__()
        self.project = self.root / 'source'
        for name in MODULE_NAMES:
            (self.project/name).mkdir(parents=True)
        self.paths = {}
        for uid,flag in [('C001',0),('C002',1)]:
            folder = self.project/'03_conic'/(uid+'_fixture')
            folder.mkdir()
            m = meta_record(uid,uid+' title')
            m['isPro'] = flag
            path = folder/'meta.json'
            path.write_text(json.dumps(m),encoding='utf-8')
            self.paths[uid] = path
        self.selection = self.root/'free.json'
        self.selection.write_text(json.dumps({
            'baselineTotal':2,'targetFree':1,'categories':{'B':1},'learningPaths':[],
            'conclusions':[{'id':'C001','title':'C001 title','module':'03_conic',
                            'chapter':'解析几何-圆锥曲线-椭圆','category':'B',
                            'pathId':None,'reason':'A reviewed geometric method.'}]
        },ensure_ascii=False),encoding='utf-8')

    def tearDown(self):
        self.tmp.__exit__(None,None,None)

    def change(self,uid,value,remove=False):
        m=json.loads(self.paths[uid].read_text(encoding='utf-8'))
        if remove:m.pop('isPro',None)
        else:m['isPro']=value
        self.paths[uid].write_text(json.dumps(m),encoding='utf-8')

    def mapped(self):
        scan=scan_repository(self.project)
        return scan,map_runtime(scan,self.root/'prepared')

    def test_actual_full_and_zip_preserve_integer_zero_one_and_other_fields(self):
        scan,runtime=self.mapped()
        self.assertEqual(runtime.errors,())
        output=self.root/'full'
        built=full.build_package(scan,runtime,output,self.root/'prepared')
        self.assertEqual(built.errors,())
        modules=self.root/'modules'
        module.slice_modules(output,modules,['analytic-geometry'],2)
        self.assertEqual(module.validate_module(modules/'analytic-geometry.zip',output),())
        records,_=validate_sources(self.project,self.selection)
        with zipfile.ZipFile(modules/'analytic-geometry.zip') as z:
            rows=json.loads(z.read('knowledge-nodes.json'))
        counts=validate_nodes(rows,records,{'C001','C002'},'ZIP')
        self.assertEqual((counts['free'],counts['licensed']),(1,1))
        for row in rows:
            if row['type']=='knowledge':
                self.assertIs(type(row['isPro']),int)
                self.assertEqual(row['title'],row['id']+' title')
            else:self.assertNotIn('isPro',row)
        self.assertEqual(full.validate_package(output),())
        audit=validate_exports(records,output,modules)
        self.assertEqual(audit['full']['total'],2)
        self.assertEqual(audit['modules']['analytic-geometry']['free'],1)

    def test_bad_explicit_source_types_fail_mapping_and_production_audit(self):
        for value in (False,True,'0','1',None,0.0,1.0,2,-1,[],{}):
            with self.subTest(value=value):
                self.change('C001',value)
                _,runtime=self.mapped()
                self.assertTrue(any('isPro' in e.message and e.path==Path('03_conic/C001_fixture/meta.json') for e in runtime.errors))
                with self.assertRaises(SelectionError):validate_sources(self.project,self.selection)

    def test_missing_source_flag_fails_current_audit_but_legacy_mapping_stays_readable(self):
        self.change('C001',None,remove=True)
        _,runtime=self.mapped()
        self.assertEqual(runtime.errors,())
        with self.assertRaises(SelectionError):validate_sources(self.project,self.selection)
        row=next(n for n in full._runtime_entities(runtime)['knowledgeNodes'] if n['id']=='C001')
        self.assertNotIn('isPro',row)

    def test_duplicate_unknown_stale_and_wrong_classifications_are_rejected(self):
        original=json.loads(self.selection.read_text(encoding='utf-8'))
        cases=[]
        m=copy.deepcopy(original);m['conclusions']*=2;m['targetFree']=2;cases.append(m)
        m=copy.deepcopy(original);m['conclusions'][0]['id']='C999';cases.append(m)
        m=copy.deepcopy(original);m['conclusions'][0]['title']='stale';cases.append(m)
        m=copy.deepcopy(original);m['conclusions'][0]['module']='00_set';cases.append(m)
        m=copy.deepcopy(original);m['conclusions'][0]['reason']='';cases.append(m)
        for value in cases:
            with self.subTest(value=value):
                self.selection.write_text(json.dumps(value),encoding='utf-8')
                with self.assertRaises(SelectionError):validate_sources(self.project,self.selection)
        self.selection.write_text(json.dumps(original),encoding='utf-8')
        self.change('C002',0)
        with self.assertRaises(SelectionError):validate_sources(self.project,self.selection)

    def test_export_shape_and_source_comparison_catch_invalid_or_missing_flags(self):
        scan,runtime=self.mapped();records,_=validate_sources(self.project,self.selection)
        original=full._runtime_entities(runtime)
        for value in (False,'1',None,1.0,3):
            entities=copy.deepcopy(original)
            next(r for r in entities['knowledgeNodes'] if r['id']=='C001')['isPro']=value
            self.assertTrue(any('isPro' in e.message for e in full._validate_entity_shapes(entities,full.JSON_FILES)))
        for mode in ('missing','wrong-value','missing-node','structural'):
            rows=copy.deepcopy(original['knowledgeNodes'])
            target=next(r for r in rows if r['id']=='C001')
            if mode=='missing':target.pop('isPro')
            elif mode=='wrong-value':target['isPro']=1
            elif mode=='missing-node':rows.remove(target)
            else:next(r for r in rows if r['type']!='knowledge')['isPro']=0
            with self.assertRaises(SelectionError):validate_nodes(rows,records,{'C001','C002'},mode)

    def test_only_flag_changes_identity_without_changing_other_dto_fields(self):
        _,before=self.mapped();old=full._runtime_entities(before)
        self.change('C001',1)
        _,after=self.mapped();new=full._runtime_entities(after)
        old_hash=full._entity_hashes(old);new_hash=full._entity_hashes(new)
        self.assertNotEqual(old_hash['knowledgeNodes']['C001'],new_hash['knowledgeNodes']['C001'])
        self.assertEqual(old_hash['knowledgeNodes']['C002'],new_hash['knowledgeNodes']['C002'])
        for data in (old,new):
            for row in data['knowledgeNodes']:row.pop('isPro',None)
        self.assertEqual(old,new)


if __name__=='__main__':unittest.main()
