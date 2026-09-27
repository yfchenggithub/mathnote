import { createHash } from 'node:crypto';
import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  writeFileSync,
} from 'node:fs';
import { basename, dirname, extname, isAbsolute, join, parse, resolve } from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

import sharp from 'sharp';

export const IMAGE_CONTRACT = Object.freeze({
  format: 'webp',
  quality: 85,
  maxWidth: 1440,
  preserveAspectRatio: true,
  upscale: false,
});

const require = createRequire(import.meta.url);
const SHARP_VERSION = require('sharp/package.json').version;
const SOURCE_EXTENSION = '.png';

export class RuntimeImagePreparationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'RuntimeImagePreparationError';
  }
}

function fail(message) {
  throw new RuntimeImagePreparationError(message);
}

function sha256File(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex');
}

function canonicalJson(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function validateJobs(value) {
  if (!value || typeof value !== 'object' || !Array.isArray(value.sources)) {
    fail('jobs JSON must contain a sources array');
  }
  const ids = new Set();
  return value.sources.map((source, index) => {
    if (!source || typeof source !== 'object') fail(`sources[${index}] must be an object`);
    for (const field of ['knowledgeId', 'sourceDirectory', 'displayDirectory']) {
      if (typeof source[field] !== 'string' || source[field].length === 0) {
        fail(`sources[${index}].${field} must be a non-empty string`);
      }
    }
    if (ids.has(source.knowledgeId)) fail(`duplicate knowledgeId: ${source.knowledgeId}`);
    ids.add(source.knowledgeId);
    return source;
  });
}

export async function prepareKnowledgeImages({ jobsPath, outputRoot }) {
  const resolvedJobsPath = resolve(jobsPath);
  const resolvedOutputRoot = resolve(outputRoot);
  if (resolvedOutputRoot === parse(resolvedOutputRoot).root) {
    fail('refusing to use a filesystem root as runtime asset output');
  }
  let jobs;
  try {
    jobs = validateJobs(JSON.parse(readFileSync(resolvedJobsPath, 'utf8')));
  } catch (error) {
    if (error instanceof RuntimeImagePreparationError) throw error;
    fail(`cannot read jobs JSON ${resolvedJobsPath}: ${error.message}`);
  }

  mkdirSync(dirname(resolvedOutputRoot), { recursive: true });
  rmSync(resolvedOutputRoot, { recursive: true, force: true });
  const staged = resolvedOutputRoot;
  const assets = [];
  try {
    mkdirSync(join(staged, 'images'), { recursive: true });
    for (const source of jobs.sort((left, right) =>
      left.knowledgeId.localeCompare(right.knowledgeId, 'en'),
    )) {
      const sourceDirectory = resolve(source.sourceDirectory);
      if (!existsSync(sourceDirectory) || !statSync(sourceDirectory).isDirectory()) {
        fail(`source image directory does not exist: ${source.displayDirectory}`);
      }
      mkdirSync(join(staged, 'images', source.knowledgeId), { recursive: true });
      const entries = readdirSync(sourceDirectory, { withFileTypes: true }).sort((left, right) =>
        left.name.localeCompare(right.name, 'en', { numeric: true }),
      );
      const outputNames = new Set();
      for (const entry of entries) {
        if (entry.name === '.gitkeep') continue;
        if (!entry.isFile()) fail(`unsupported source image entry: ${source.displayDirectory}/${entry.name}`);
        if (extname(entry.name).toLowerCase() !== SOURCE_EXTENSION) {
          fail(`unsupported source image extension: ${source.displayDirectory}/${entry.name}`);
        }
        const outputName = `${parse(entry.name).name}.webp`;
        if (outputNames.has(outputName.toLowerCase())) {
          fail(`runtime image name collision: ${source.knowledgeId}/${outputName}`);
        }
        outputNames.add(outputName.toLowerCase());
        const sourcePath = join(sourceDirectory, entry.name);
        const relativeOutput = `images/${source.knowledgeId}/${outputName}`;
        const outputPath = join(staged, 'images', source.knowledgeId, outputName);
        mkdirSync(dirname(outputPath), { recursive: true });

        const inputMetadata = await sharp(sourcePath, { failOn: 'error' }).metadata();
        if (inputMetadata.format !== 'png' || !inputMetadata.width || !inputMetadata.height) {
          fail(`source is not a decodable PNG: ${source.displayDirectory}/${entry.name}`);
        }
        let pipeline = sharp(sourcePath, { failOn: 'error' });
        if (inputMetadata.width > IMAGE_CONTRACT.maxWidth) {
          pipeline = pipeline.resize({ width: IMAGE_CONTRACT.maxWidth, withoutEnlargement: true });
        }
        await pipeline.webp({ quality: IMAGE_CONTRACT.quality }).toFile(outputPath);

        const outputMetadata = await sharp(outputPath, { failOn: 'error' }).metadata();
        if (
          outputMetadata.format !== 'webp' ||
          !outputMetadata.width ||
          !outputMetadata.height ||
          outputMetadata.width > IMAGE_CONTRACT.maxWidth ||
          outputMetadata.width > inputMetadata.width
        ) {
          fail(`runtime WebP validation failed: ${relativeOutput}`);
        }
        const expectedWidth = Math.min(inputMetadata.width, IMAGE_CONTRACT.maxWidth);
        const expectedHeight = Math.round((inputMetadata.height * expectedWidth) / inputMetadata.width);
        if (outputMetadata.width !== expectedWidth || Math.abs(outputMetadata.height - expectedHeight) > 1) {
          fail(`runtime WebP aspect ratio validation failed: ${relativeOutput}`);
        }
        if (statSync(outputPath).size === 0) fail(`runtime WebP is empty: ${relativeOutput}`);

        assets.push({
          knowledgeId: source.knowledgeId,
          source: `${source.displayDirectory}/${entry.name}`.replaceAll('\\', '/'),
          output: relativeOutput,
          sourceSha256: sha256File(sourcePath),
          outputSha256: sha256File(outputPath),
          sourceWidth: inputMetadata.width,
          sourceHeight: inputMetadata.height,
          width: outputMetadata.width,
          height: outputMetadata.height,
          bytes: statSync(outputPath).size,
        });
      }
    }

    assets.sort((left, right) => left.output.localeCompare(right.output, 'en'));
    const manifest = {
      schemaVersion: 1,
      contract: IMAGE_CONTRACT,
      tool: { name: 'sharp', version: SHARP_VERSION },
      assets,
    };
    writeFileSync(join(staged, 'manifest.json'), canonicalJson(manifest), 'utf8');
    return manifest;
  } catch (error) {
    try {
      rmSync(staged, { recursive: true, force: true });
    } catch {
      // Preserve the original preparation error; the next full rebuild does not
      // consume abandoned transaction directories.
    }
    throw error;
  }
}

function parseArguments(argv) {
  const options = {};
  for (let index = 0; index < argv.length; index += 2) {
    const option = argv[index];
    const value = argv[index + 1];
    if (!value || !['--jobs', '--output'].includes(option)) {
      fail(`Usage: node ${fileURLToPath(import.meta.url)} --jobs PATH --output PATH`);
    }
    options[option === '--jobs' ? 'jobsPath' : 'outputRoot'] = value;
  }
  if (!options.jobsPath || !options.outputRoot) {
    fail(`Usage: node ${fileURLToPath(import.meta.url)} --jobs PATH --output PATH`);
  }
  return options;
}

async function main() {
  const result = await prepareKnowledgeImages(parseArguments(process.argv.slice(2)));
  const totalBytes = result.assets.reduce((sum, asset) => sum + asset.bytes, 0);
  console.log(`Prepared WebP images: ${result.assets.length}`);
  console.log(`Prepared bytes: ${totalBytes}`);
  console.log(`Tool: ${result.tool.name} ${result.tool.version}`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  main().catch((error) => {
    console.error(error.stack ?? `${error.name}: ${error.message}`);
    process.exitCode = 1;
  });
}
