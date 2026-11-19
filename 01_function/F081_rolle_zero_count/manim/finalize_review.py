"""Record local acceptance after guarded export into this UID's images/."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[3]
UID=Path(__file__).resolve().parent.parent
BUILD=ROOT/'build/manim/F081-production-20261119'
sys.path.insert(0,str(ROOT/'scripts/manim'))
from verify_gif import verify_gif

base=json.loads((BUILD/'baseline.json').read_text(encoding='utf-8'))
changed=[p for p,h in base.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
assert not changed,changed
tests=json.loads((BUILD/'math_test_result.json').read_text(encoding='utf-8'))
assert tests['status']=='PASS' and tests['returncode']==0
assets=[]
for name in ['rolle_equal_height','rolle_zero_count']:
    formal=UID/'images'/(name+'.gif')
    staged=BUILD/'F081'/name/(name+'.gif')
    audit=json.loads((BUILD/'review'/name/'frame_audit.json').read_text(encoding='utf-8'))
    digest=hashlib.sha256(formal.read_bytes()).hexdigest()
    assert digest==hashlib.sha256(staged.read_bytes()).hexdigest()==audit['gif_sha256']
    technical=verify_gif(formal)
    assert technical['valid']
    assets.append({'path':formal.relative_to(ROOT).as_posix(),'sha256':digest,'technical':technical,'all_frame_audit':audit,'gates':{'M':'PASS','V_local':'PASS','T':'PASS','G':'PASS','D_android':'PENDING'},'real_keyframes_reviewed':audit['review_images']})
report={'uid':'F081','status':'LOCAL PRODUCTION PASS','math_tests':tests,'assets':assets,'preserved_baseline_files':len(base),'changed_baseline_files':changed,'source_location':'01_function/F081_rolle_zero_count/manim','user_visual':'PENDING','android_device':'PENDING','final_freeze':'PENDING','formal_images_placement':'PASS; explicitly requested by user; guarded exporter used without overwrite','publisher_content_package':'NOT RUN','sync':'NOT RUN','publisher_contract_review':['scripts/manim/production.py guards direct images placement and refuses existing GIF names.','scripts/zhishu/asset_preparation.py discovers direct PNG/GIF resources and keeps GIF bytes.','scripts/zhishu/runtime_mapping.py preserves each GIF filename in resource URI.'],'footer':['查结论 · 看图解 · 学证明｜知树 App','公众号 ok-shuxue｜获取入口'],'visual_evidence':'build/manim/F081-production-20261119/review/','notes':['GIF rendering does not modify six TeX sections, metadata, TikZ or PDFs.','Two independent mathematical models were built from the UID sources.','Tiny footer raster differences arise from MP4 compression and palette quantization; all-frame ink-mask presence and stability were verified.','No other UID, shared tool, formal package, Sync or APK was changed or built.']}
(UID/'manim/VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
text='''# F081 GIF 本地验收

状态：LOCAL PRODUCTION PASS。用户视觉验收、Android真机验收、FINAL FREEZE均为PENDING。按用户明确指令，使用Task 13F冻结导出器将两幅新GIF放入本UID的images；没有覆盖已有资源，也没有运行Publisher、Content Package、Sync或APK构建。

| GIF | 内容 | 规格 |
| --- | --- | --- |
'''
for a in assets:
    k=a['technical'];name=Path(a['path']).name
    description='等高端点：上拱、平走、下凹、非中点驻点及多次起伏' if 'equal' in name else '零点交错与三次函数参数变化；相切点只数一次'
    text+=f'| ../images/{name} | {description} | {k["width"]}×{k["height"]}，{k["frame_count"]}帧，{k["duration_seconds"]}秒，无限循环，{k["bytes"]/1048576:.2f} MiB |'+chr(10)
text+='''
数学：5组模型测试通过。核对等高端点在整个连续形变中不变、驻点严格位于内部且导数为零、恒定情形、多驻点波形、三次方程所有参数分支的不同实根数与零点交错，以及曲线窗口内的真实采样坐标。一般罗尔定理的条件全程保留；动画只展示典型图形，不替代PDF中的一般证明。

本地视觉与教学：检查28张真实GIF关键帧和运动中间帧，覆盖首尾、平走、上下极值、非中点驻点、四个水平切点、相切重根和参数运动。消除临时强调点残留；文字先切换到适用于运动过程的说明，再改变参数。文字采用短淡入淡出，避免汉字长时间变形。区间高亮、投影和切线均来自真实坐标。

全帧技术：两幅GIF均完整解码、真实多帧、12fps导出、无限循环，无黑帧。全部帧检查外侧安全区域无越界墨迹；底部两行文案全程存在，比较文字墨迹结构与像素误差以容许视频压缩/调色板量化。源GIF与images中的副本SHA-256一致，详细结果见VALIDATION.json。

六段TeX、meta.json、main.tex、PDF及已有23幅TikZ共33个基线文件哈希均保持不变。数学模型、场景、分镜、测试与验收脚本均在本目录；视频、暂存GIF、实际关键帧和日志在build/manim/F081-production-20261119。无已知本地制作问题；真机播放和用户视觉效果尚未确认，不能标记最终冻结。
'''
(UID/'manim/README.md').write_text(text,encoding='utf-8')
print(json.dumps({'status':report['status'],'assets':[{'path':a['path'],'frames':a['technical']['frame_count'],'seconds':a['technical']['duration_seconds'],'bytes':a['technical']['bytes']} for a in assets],'baseline_unchanged':len(base)},ensure_ascii=False,indent=2))
