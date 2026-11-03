"""C072-local review of the rendered midpoint revision; never publishes assets."""
from pathlib import Path
import hashlib
import json
import math
import sys

import numpy as np
from PIL import Image
from manim import tempconfig


def main():
    root = Path(__file__).resolve().parents[3]
    work = root / 'build/manim/C072/midpoint_revision'
    evidence = root / 'build/manim/C072/midpoint_review'
    gif = work / 'midpoint_revision.gif'
    records = json.loads((work/'media/c072_state_audit.json').read_text())
    for r in records:
        P, M, N, A, B = (r[k] for k in ('P', 'M', 'N', 'A', 'B'))
        assert all(math.isfinite(v) for q in (P, M, N, A, B) for v in q)
        assert math.isclose(N[0]**2, 2*N[1], abs_tol=1e-10)
        assert math.isclose(N[0], P[0], abs_tol=1e-10)
        assert math.isclose(N[1], (P[1]+M[1])/2, abs_tol=1e-10)
        assert r['PN'] > 0 and r['NM'] > 0
        assert math.isclose(r['PN'], r['NM'], abs_tol=1e-10)
        assert r['displayed_PN'] == r['displayed_NM']
        det = abs((A[0]-P[0])*(B[1]-P[1])-(B[0]-P[0])*(A[1]-P[1]))/2
        assert math.isclose(det, abs(A[0]-B[0])**3/8, abs_tol=1e-10)

    # Check actual MathTex label rectangles against all graph strokes throughout
    # the motion rectangle. This supplements inspection of the decoded GIF.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from model import state, midpoint_state
    with tempconfig({'media_dir': str(work/'media')}):
        from scene_batch import eq
        extents = {name:(eq(name,42).width/2, eq(name,42).height/2)
                   for name in ('A','B','P','M','N')}
    u = np.linspace(-2, 2, 1001)
    curve = np.column_stack((1.85*u, .65+1.85*u*u/2))
    min_margin = 100.
    checked = 0
    for t in np.linspace(-.45,.45,41):
        for d in np.linspace(.8,1.3,41):
            A,B,P,M = state(t,d)
            N,_,_ = midpoint_state(t,d)
            xy = lambda q: np.array([1.85*q[0],1.85*q[1]+.65])
            strokes = [curve]
            for Q,R in ((P,A),(P,B),(A,B),(P,M)):
                f = np.linspace(0,1,301)[:,None]
                strokes.append(xy(Q)[None,:]*(1-f)+xy(R)[None,:]*f)
            cloud = np.vstack(strokes)
            centers = {'A':xy(A)+[-.38,-.2], 'B':xy(B)+[.36,-.16],
                       'P':xy(P)+[0,-.4], 'M':xy(M)+[0,.4],
                       'N':xy(N)+[(-.45 if t>=0 else .45),.36-.6*abs(t)]}
            for name,c in centers.items():
                hx,hy = extents[name]
                assert -4.5<c[0]-hx<c[0]+hx<4.5
                assert -8<c[1]-hy<c[1]+hy<8
                clearance = np.maximum(np.abs(cloud[:,0]-c[0])-hx,
                                       np.abs(cloud[:,1]-c[1])-hy)
                assert np.min(clearance)>0, (t,d,name,float(np.min(clearance)))
                min_margin = min(min_margin,float(np.min(clearance)))
                checked += 1

    im = Image.open(gif)
    footer = None
    first = None
    durations = []
    footer_errors = []
    footer_overlaps = []
    gold_errors = []
    record_times = np.array([r['time'] for r in records])
    for k in range(im.n_frames):
        im.seek(k)
        frame = im.convert('RGB')
        crop = frame.crop((0,918,576,1010))
        if first is None:
            first, footer = frame.copy(), crop.copy()
        # MP4 compression and GIF quantization perturb edge pixels of static
        # text. Require the same text silhouette and low error, not byte identity.
        ca,fa = np.asarray(crop).astype(float),np.asarray(footer).astype(float)
        error = float(np.mean(np.abs(ca-fa)))
        cm,fm = ca.mean(axis=2)<200,fa.mean(axis=2)<200
        overlap = float((cm&fm).sum()/max(1,(cm|fm).sum()))
        assert error<2 and overlap>.94, (k,error,overlap)
        footer_errors.append(error)
        footer_overlaps.append(overlap)
        # Inspect the actual gold dot, including its reveal transition, against
        # the independently recorded curve intersection. Detect color direction
        # so a partially faded gold pixel is still recognizable.
        if 96<=k<=202:
            r = records[int(np.argmin(np.abs(record_times-k/12)))]
            nx,ny = r['N']
            expected = np.array([(4.5+1.85*nx)*64,
                                 (8-(.65+1.85*ny))*64])
            x,y = np.rint(expected).astype(int)
            patch = np.asarray(frame).astype(float)[y-12:y+13,x-12:x+13]
            vector = np.array([247,248,250])-np.array([183,125,18])
            delta = np.array([247,248,250])-patch
            cosine = (delta@vector)/(np.linalg.norm(delta,axis=2)*np.linalg.norm(vector)+1e-9)
            alpha = (delta@vector)/(vector@vector)
            yy,xx = np.where((cosine>.995)&(alpha>.15))
            assert len(xx)>=5, ('missing rendered N',k,len(xx))
            center = np.array([x-12+xx.mean(),y-12+yy.mean()])
            error = float(np.linalg.norm(center-expected))
            assert error<5, ('rendered N displaced',k,error)
            gold_errors.append(error)
        durations.append(im.info['duration'])
    loop_error = float(np.abs(np.asarray(first).astype(float)-np.asarray(frame).astype(float)).mean())
    same_loop = loop_error<1
    assert same_loop, loop_error
    samples = [0,42,78,99,112,145,170,184,205,im.n_frames-1]
    for k in samples:
        im.seek(k)
        im.convert('RGB').save(evidence/f'key_{k:03}.png')
    # All-frame contact sheets at one fifth size, in addition to full-size keys.
    for start in range(0,im.n_frames,36):
        contact = Image.new('RGB',(6*192,6*342),'#FFFFFF')
        for j,k in enumerate(range(start,min(start+36,im.n_frames))):
            im.seek(k)
            thumb = im.convert('RGB').resize((192,342))
            contact.paste(thumb,((j%6)*192,(j//6)*342))
        contact.save(evidence/f'all_frames_{start:03}.png')

    protected = json.loads((evidence/'protected_baseline.json').read_text())
    for name,digest in protected.items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest, name
    report = dict(mathematical_records=len(records), label_rectangles_checked=checked,
        min_graph_label_clearance_units=min_margin, frame_count=im.n_frames,
        duration_seconds=sum(durations)/1000, dimensions=im.size,
        footer_present_all_frames=True, footer_max_mean_pixel_error=max(footer_errors),
        footer_min_text_mask_iou=min(footer_overlaps),
        first_last_visually_equivalent=same_loop, first_last_mean_pixel_error=loop_error,
        rendered_N_frames_checked=len(gold_errors), max_rendered_N_error_px=max(gold_errors),
        protected_files_unchanged=len(protected), sha256=hashlib.sha256(gif.read_bytes()).hexdigest())
    (evidence/'frame_review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
