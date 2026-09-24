import fs from 'node:fs/promises';
import path from 'node:path';
import {finalizePresentation} from 'file:///C:/Users/Kenpo/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations/container_tools/artifact_tool_utils.mjs';
const ROOT=process.cwd(),TMP=path.join(ROOT,'build_codex/slate_talk/animated_deck_v10');
const SKILL='C:/Users/Kenpo/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations';
process.env.RUNTIME_NODE_MODULES='C:/Users/Kenpo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const finalPath=path.join(ROOT,'output/presentations/Oriented_Powder_8min_Animated_v10.pptx');
await fs.mkdir(path.dirname(finalPath),{recursive:true});
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:path.join(TMP,'candidate.pptx'),finalPath,
 pythonExecutable:'C:/Users/Kenpo/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
 integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','16'],
 explicitTotalSlideCount:26,requiredNativeTableOwnerSlides:[16],requiredNativeChartOwnerSlides:[12,13,14,15,16,17,18,26],
 approvedSourceFigureExceptionSlides:[12,13,14,15],requiredEmbeddedWorkbookChartOwnerSlides:[16,17,18,26],materializeLiteralChartWorkbooks:false,
 fontPolicy:{basis:'reference',families:['Arial','Calibri'],referencePath:path.join(ROOT,'presentation_asset_library/releases/2026-09-10_v9/presentation/Oriented_Powder_8min_Animated_v9.pptx'),referenceSha256:'0feca65d8e57c764666012cc75cd880da660fd1fea12eedba0cec69193c2cec3'},
 verifyArtifactToolImport:true,receiptPath:path.join(TMP,'final_validation.json')});
console.log(JSON.stringify({finalPath:result.finalPath,sha256:result.finalSha256,bytes:result.byteCount}));
