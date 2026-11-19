"""Validate guarded placement of the new nine-paths GIF without changing old assets."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[3]
UID=Path(__file__).resolve().parent.parent
BUILD=ROOT/'build/manim/F081-nine-paths-20261119'
NAME='zero_derivative_nine_paths'
sys.path.insert(0,str(ROOT/'scripts/manim'))
from verify_gif import verify_gif

base=json.loads((BUILD/'baseline.json').read_text(encoding='utf-8'))
changed=[p for p,h in base.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
assert not changed,changed
tests=json.loads((BUILD/'math_test_result.json').read_text(encoding='utf-8'))
assert tests['status']=='PASS' and tests['returncode']==0
audit=json.loads((BUILD/'review/frame_audit.json').read_text(encoding='utf-8'))
assert audit['status']=='PASS'
asset=UID/'images'/(NAME+'.gif')
staged=BUILD/'F081'/NAME/(NAME+'.gif')
digest=hashlib.sha256(asset.read_bytes()).hexdigest()
assert digest==audit['gif_sha256']==hashlib.sha256(staged.read_bytes()).hexdigest()
technical=verify_gif(asset);assert technical['valid']
states=json.loads((BUILD/'key_states.json').read_text(encoding='utf-8'))
origins=[s for s in states if s['name'].endswith('_origin')]
assert len(origins)==9 and all(s['values']['slope']==0 for s in origins)
report={'uid':'F081','asset':asset.relative_to(ROOT).as_posix(),'status':'LOCAL PRODUCTION PASS','sha256':digest,'math_tests':tests,'technical':technical,'all_frame_audit':audit,'nine_key_states':origins,'gates':{'M_mathematics':'PASS','V_local_visual':'PASS','T_teaching':'PASS','G_technology':'PASS','D_android_device':'PENDING'},'user_visual':'PENDING','final_freeze':'PENDING','images_placement':'PASS: user explicitly requested; guarded exporter, no overwrite','publisher_content_package':'NOT RUN','sync':'NOT RUN','baseline_files_preserved':len(base),'baseline_files_changed':changed,'mathematical_qualifications':['At 0 both definitions give zero, so x<=0/x>0 and x<0/x>=0 conventions are equivalent.','These are nine typical combinations with each side having fixed derivative sign; they do not exhaust all differentiable functions.','One-sided plateaus may give non-strict extrema; the movie does not equate no reversal with no extremum.','The models explain the meaning of f_prime(0)=0; they are not nine statements that all Rolle hypotheses hold.'],'evidence_directory':'build/manim/F081-nine-paths-20261119/review/'}
(UID/'manim/NINE_PATHS_VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
text=f'''# 导数为零的九种走向：本地验收

交付：../images/{NAME}.gif。{technical['width']}×{technical['height']}，{technical['frame_count']}帧，{technical['duration_seconds']}秒，约{technical['bytes']/1048576:.2f} MiB，12fps导出、无限循环。

状态：LOCAL PRODUCTION PASS。数学、桌面视觉、教学表达、技术格式为PASS；用户视觉、Android真机、FINAL FREEZE为PENDING。已按用户要求使用冻结导出器放入本UID的images目录，没有覆盖已有GIF。没有运行Publisher、Content Package、Sync或APK构建。

数学模型来自本UID的九种走向小节、补充验证和用户给出的分段三次函数。编号按正式文档的升、平、降顺序。九种系数对逐一验证，5组数学测试PASS；原点差商满足绝对值≤h²，左右同时趋于0。测试还核对每侧的增减、所有扫描位置的切线以及水平段与非严格极值的区别。③、⑦体现严格的增减反向；含水平段时只说明进出平路，不误说没有极值。

教学与视觉：逐一展示9幅同尺度大图，真实追踪点和切线穿过原点，随后给出差商解释和九宫格汇总。系数、方向文字和曲线同步切换；不使用文字变形或伪造中间图像。检查{len(audit['keyframes'])}张真实关键帧，覆盖9个原点状态、9个右侧状态、9个运动中间状态、首尾、差商和汇总；标签、曲线、公式与品牌区域未发现遮挡或裁切。九宫格编号与系数已放大。第一帧直接显示第1种函数。

全帧技术检查：GIF完整解码，真实多帧，无黑帧，80–90ms帧时长，无限循环；所有帧的外侧安全边无深色越界像素，底部两行文案全程固定。以文字墨迹结构及像素误差检查品牌区域，允许视频压缩和调色板量化的小差异。正式GIF和已验收暂存GIF哈希完全一致。

原有{len(base)}个基线文件哈希均保持不变，包括知识源、TikZ、PDF、PNG、原有GIF和既有Manim文件。只新增本片模型、Scene、测试、分镜、验收脚本、验收记录及1幅GIF。数学模型见model_nine.py，场景见scene_nine.py；完整关键帧与日志在build/manim/F081-nine-paths-20261119，详细参数及哈希见NINE_PATHS_VALIDATION.json。
'''
(UID/'manim/NINE_PATHS_ACCEPTANCE.md').write_text(text,encoding='utf-8')
print(json.dumps({'status':report['status'],'asset':report['asset'],'frames':technical['frame_count'],'seconds':technical['duration_seconds'],'bytes':technical['bytes'],'baseline_unchanged':len(base)},ensure_ascii=False,indent=2))
