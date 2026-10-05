#!/usr/bin/env python3
"""Final artifact audit and hashes. Does not qualify the partial fit as hardware equality."""
import argparse
import json
import math
from pathlib import Path
import struct

import numpy as np
from scipy.optimize import brentq

from fit import HERE,sha256,write_json
from reference import Reference


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library',required=True)
    args=parser.parse_args()
    fit=json.loads((HERE/'jensen-fit.json').read_text(encoding='utf-8'))
    profiles=json.loads((HERE/'profiles.json').read_text(encoding='utf-8'))
    validation=json.loads((HERE/'validation.json').read_text(encoding='utf-8'))
    previews=json.loads((HERE/'preview-manifest.json').read_text(encoding='utf-8'))
    assert fit['targets_sha256']==sha256(HERE/'targets.csv')
    assert fit['fixture_sha256']==sha256(HERE/'fixture.json')
    for name,digest in fit['source_sha256'].items():assert sha256(HERE/name)==digest
    assert validation['fit_sha256']==sha256(HERE/'jensen-fit.json')
    assert validation['profiles_sha256']==sha256(HERE/'profiles.json')
    assert profiles['fit_sha256']==sha256(HERE/'jensen-fit.json')
    assert profiles['script_sha256']==sha256(HERE/'create_profiles.py')
    assert previews['profiles_sha256']==sha256(HERE/'profiles.json')
    assert previews['render_script_sha256']==sha256(HERE/'render_and_plot.py')
    wavs=[]
    for path in (HERE/'audio').glob('*.wav'):
        data=path.read_bytes()
        assert data[:4]==b'RIFF' and data[8:12]==b'WAVE'
        assert struct.unpack_from('<I',data,4)[0]+8==len(data)
        fmt,channels,rate=struct.unpack_from('<HHI',data,20)
        assert fmt==3 and rate==48000 and channels in (1,2)
        audio=np.frombuffer(data,dtype='<f4',offset=44)
        assert np.all(np.isfinite(audio))
        wavs.append(dict(file=str(path.relative_to(HERE)),frames=len(audio)//channels,
                         channels=channels,rate=rate,peak=float(np.max(abs(audio))),sha256=sha256(path)))
    assert len(wavs)==7
    reference=Reference(args.library)
    p=fit['best']['parameters']
    one_percent=brentq(lambda level:reference.tone(p,20,level,8192)[0]['thd_percent']-1,
                      18,23,xtol=1e-7)
    assert abs(one_percent-fit['onepercent_20hz_primary_dbu'])<1e-3
    # Probe all profile rates and confirm ordered thresholds and explicit normalization.
    anchors=[]
    for name in ('60s','80s','00s'):
        entry=profiles['profiles'][name]
        m=reference.tone(entry['parameters'],20,entry['measured_20hz_1percent_dbu'],8192)[0]
        threshold=20*math.log10(m['source_rms_v']*math.sqrt(2)/entry['source_volts_per_fs'])
        assert abs(m['thd_percent']-1)<.001
        assert abs(threshold-entry['derivation']['target_one_percent_dbfs'])<.001
        anchors.append(dict(profile=name,dbfs_peak=threshold,thd_percent=m['thd_percent']))
    assert anchors[0]['dbfs_peak']<anchors[1]['dbfs_peak']<anchors[2]['dbfs_peak']
    artifacts={str(path.relative_to(HERE)):sha256(path) for path in HERE.rglob('*')
               if path.is_file() and '__pycache__' not in path.parts and path.name not in
               ('SHA256SUMS','artifact-audit.json')}
    write_json(HERE/'artifact-audit.json',dict(
        result='PASS artifact identity and rerendered anchor checks; partial fit remains partial',
        source_sha256=sha256(Path(__file__)),fit_repeated_onepercent_dbu=one_percent,
        anchors=anchors,wavs=wavs,artifacts=artifacts))
    paths=sorted(path for path in HERE.rglob('*') if path.is_file() and
                 '__pycache__' not in path.parts and path.name!='SHA256SUMS')
    with (HERE/'SHA256SUMS').open('w',encoding='utf-8',newline='\n') as stream:
        for path in paths:stream.write(sha256(path)+'  '+str(path.relative_to(HERE))+'\n')
    print('PASS:',len(paths),'hashed artifacts; 7 WAVs; 3 ordered profile anchors;',one_percent,'dBu Jensen 1% point')


if __name__=='__main__':main()
