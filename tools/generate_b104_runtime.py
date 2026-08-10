#!/usr/bin/env python3
from __future__ import annotations
import argparse,collections,json,re,shutil,hashlib
from pathlib import Path

def load_map(path:Path):
    import base64,zlib
    raw=base64.b85decode(path.read_text(encoding="ascii").strip())
    return json.loads(zlib.decompress(raw).decode("utf-8"))


def enc_pack(v:str)->str:
    return v.replace('~','~T').replace('"','~Q').replace('|','~P')

def helper_info(s:str):
    pm=re.search(r'string\s+(u5k_[0-9a-f]+)_extract\$\(string pack_name\$, int entry\$\)',s,re.I)
    am=re.search(r'UIShell\.ActivateInterface\("ui:interfaces:u5k_text:(u5k_cv_[0-9a-f]+)"',s,re.I)
    return (pm.group(1),am.group(1)) if pm and am else (None,None)

def append_pack(ko_root:Path,base:str,pack:str,displays:list[str]):
    gp=ko_root/'ui/interfaces/u5k_text'/(base+'.gas')
    s=gp.read_bytes().decode('cp949')
    if f'n:{pack}]' in s: raise RuntimeError(f'duplicate pack {pack}')
    text='|'.join(enc_pack(x) for x in displays)
    block=(f'\r\n[t:edit_box,n:{pack}]\r\n{{\r\n    pass_through = True;\r\n    common_control = False;\r\n    common_template = ;\r\n    rect = 0,0,1,1;\r\n    texture = ;\r\n    alpha = 0;\r\n    visible = False;\r\n    text = "{text}";\r\n    font_type = b_gui_fnt_12p_Flat-Brush;\r\n    font_color = 0xffffffff;\r\n    font_size = 12;\r\n    permanent_focus = False;\r\n    has_pixel_limit = False;\r\n    max_string_size = 16384;\r\n    has_border = False;\r\n}}\r\n')
    pos=s.rfind('}')
    if pos<0: raise RuntimeError(f'GAS root close missing: {gp}')
    gp.write_bytes((s[:pos]+block+s[pos:]).encode('cp949'))

def strip_comments(s:str)->str:
    out=[];i=0;n=len(s);inq=False;esc=False
    while i<n:
        c=s[i]
        if inq:
            out.append(c)
            if esc:esc=False
            elif c=='\\':esc=True
            elif c=='"':inq=False
            i+=1;continue
        if c=='"':inq=True;out.append(c);i+=1;continue
        if c=='/' and i+1<n and s[i+1]=='/':
            i+=2
            while i<n and s[i] not in '\r\n':i+=1
            continue
        if c=='/' and i+1<n and s[i+1]=='*':
            i+=2
            while i+1<n and not(s[i]=='*' and s[i+1]=='/'):
                if s[i] in '\r\n':out.append(s[i])
                i+=1
            i+=2;continue
        out.append(c);i+=1
    return ''.join(out)

def patch_options(laz:Path,br:Path,ko:Path,optmap:dict[str,str]):
    raw_pat=re.compile(r'\badd_keyword\$\(\s*"((?:\\.|[^"\\])*)"\s*,',re.I)
    st=collections.Counter()
    for p in sorted((laz/'world/global/conversations').glob('*.skrit')):
        if p.name.casefold() == 'conversation_debugger_npc.skrit':
            continue
        s=p.read_bytes().decode('cp949'); sc=strip_comments(s); raws=[]
        for m in raw_pat.finditer(sc):
            raw=m.group(1).replace('\\"','"').replace('\\\\','\\')
            if raw not in raws:raws.append(raw)
        trans=[(raw,optmap[raw]) for raw in raws if raw in optmap and optmap[raw]!=raw]
        if not trans:continue
        prefix,base=helper_info(s)
        if not prefix or not base: raise RuntimeError(f'helper missing for translated options: {p}')
        pack=base+'_b104opt_pack_0001';append_pack(ko,base,pack,[x[1] for x in trans])
        for idx,(raw,_) in enumerate(trans):
            call=f'{prefix}_text_0$("{pack}", {idx})'
            patt=re.compile(r'\badd_keyword\$\(\s*"'+re.escape(raw)+r'"\s*,',re.I)
            s,na=patt.subn(f'add_keyword$({call},',s)
            patr=re.compile(r'\bremove_keyword\$\(\s*"'+re.escape(raw)+r'"\s*\)',re.I)
            s,nr=patr.subn(f'remove_keyword$({call})',s)
            st['add_calls']+=na;st['remove_calls']+=nr
        p.write_bytes(s.encode('cp949'));st['files']+=1;st['packs']+=1;st['keys']+=len(trans)
    # Trainer UI: append two labels to the existing u5k_tr_pack_0001 and use those labels for display + comparison.
    trainer_gas=laz/'ui/interfaces/lazarus/ui_lazarus_trainer.gas'
    gs=trainer_gas.read_bytes().decode('cp949')
    old_tail='|아무도 없음|예|아니오|계속";'
    new_tail='|아무도 없음|예|아니오|계속|파괴|보호";'
    if gs.count(old_tail)!=1: raise RuntimeError('trainer GAS pack tail not found')
    trainer_gas.write_bytes(gs.replace(old_tail,new_tail,1).encode('cp949'))
    trainer=br/'world/global/skrits/k_inc_pb_trainer.skrit'
    ts=trainer.read_bytes().decode('cp949')
    replacements=[
      ('trainer_kw_list$.AddElement("Destruction", kw_index$);','trainer_kw_list$.AddElement(u5k_cc04759d2d_text_0$("u5k_tr_pack_0001", 44), kw_index$);'),
      ('trainer_kw_list$.AddElement("Protection", kw_index$);','trainer_kw_list$.AddElement(u5k_cc04759d2d_text_0$("u5k_tr_pack_0001", 45), kw_index$);'),
      ('selected_keyword$ == "Destruction"','selected_keyword$ == u5k_cc04759d2d_text_0$("u5k_tr_pack_0001", 44)'),
      ('selected_keyword$ == "Protection"','selected_keyword$ == u5k_cc04759d2d_text_0$("u5k_tr_pack_0001", 45)'),
    ]
    for old,new in replacements:
        if ts.count(old)!=1: raise RuntimeError(f'trainer token count unexpected: {old}')
        ts=ts.replace(old,new,1)
    trainer.write_bytes(ts.encode('cp949'))
    st['trainer_display']=2;st['trainer_compare']=2
    return st

def patch_dynamic(laz:Path,ko:Path,nmap:dict[str,str]):
    sgpat=re.compile(r'setGlobalString\$\(\s*"([^"]+)"\s*,\s*"((?:\\.|[^"\\])*)"\s*\)',re.I)
    assignpat_tpl=r'(?m)(\b[A-Za-z_][A-Za-z0-9_]*\$\s*=\s*)"{raw}"(\s*;)'
    st=collections.Counter()
    for p in sorted((laz/'world/global/conversations').glob('*.skrit')):
        s=p.read_bytes().decode('cp949');found=[]
        for m in sgpat.finditer(s):
            raw=m.group(2).replace('\\"','"').replace('\\\\','\\');ko_val=nmap.get(raw)
            if not ko_val and raw.endswith("'s") and raw[:-2] in nmap:ko_val=nmap[raw[:-2]]+'의'
            if ko_val and (raw,ko_val) not in found:found.append((raw,ko_val))
        if not found:continue
        prefix,base=helper_info(s)
        if not prefix or not base:continue
        pack=base+'_b104dyn_pack_0001';append_pack(ko,base,pack,[v for _,v in found])
        for idx,(raw,_) in enumerate(found):
            call=f'{prefix}_text_0$("{pack}", {idx})'
            pat=re.compile(r'(setGlobalString\$\(\s*"[^"]+"\s*,\s*)"'+re.escape(raw)+r'"(\s*\))',re.I)
            s,n1=pat.subn(lambda m:m.group(1)+call+m.group(2),s)
            pat2=re.compile(assignpat_tpl.format(raw=re.escape(raw)),re.I)
            s,n2=pat2.subn(lambda m:m.group(1)+call+m.group(2),s)
            st['setglobal']+=n1;st['assignments']+=n2
        p.write_bytes(s.encode('cp949'));st['files']+=1;st['packs']+=1;st['names']+=len(found)
    return st

def patch_system(laz:Path,br:Path):
    gas=laz/'ui/interfaces/backend/data_bar/data_bar.gas';s=gas.read_bytes().decode('cp949')
    pack='u5k_b104_pack_0001';vals=['주문이 무효화되었다...','파울리네이','아스타로스','노스펜토르']
    if f'n:{pack}]' not in s:
        text='|'.join(enc_pack(x) for x in vals)
        block=(f'\r\n[t:edit_box,n:{pack}]\r\n{{\r\n    pass_through = True;\r\n    common_control = False;\r\n    common_template = ;\r\n    rect = 0,0,1,1;\r\n    texture = ;\r\n    alpha = 0;\r\n    visible = False;\r\n    text = "{text}";\r\n    font_type = b_gui_fnt_12p_Flat-Brush;\r\n    font_color = 0xffffffff;\r\n    font_size = 12;\r\n    permanent_focus = False;\r\n    has_pixel_limit = False;\r\n    max_string_size = 16384;\r\n    has_border = False;\r\n}}\r\n')
        pos=s.rfind('}');built=s[:pos]+block+s[pos:];built=built.replace('    has_border = False;\r\n}\r\n}', '    has_border = False;\r\n}}\r\n}', 1);gas.write_bytes(built.encode('cp949'))
    p=br/'world/contentdb/components/spells/spell.skrit';s=p.read_bytes().decode('latin1');s=s.replace('report.screen("fizzle...");','report.screen(u5k_7b1314b530_text_0$("u5k_b104_pack_0001", 0));');p.write_bytes(s.encode('latin1'))
    p=laz/'world/global/skrits/k_inc_shadowlords.skrit';s=p.read_bytes().decode('latin1')
    for en,idx in [('Faulenei',1),('Astaroth',2),('Nosfentor',3)]:s=s.replace(f'SSetScreenName("{en}")',f'SSetScreenName(u5k_cb4592828f_text_0$("u5k_b104_pack_0001", {idx}))')
    s=s.replace('SSetScreenName("Faulinei")','SSetScreenName(u5k_cb4592828f_text_0$("u5k_b104_pack_0001", 1))')
    p.write_bytes(s.encode('latin1'))

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def make_replacements(base:Path,work:Path,out:Path)->int:
    if out.exists():shutil.rmtree(out)
    n=0
    for p in work.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(work);bp=base/rel
        if not bp.exists() or bp.read_bytes()!=p.read_bytes():
            q=out/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);n+=1
    return n

def main():
    ap=argparse.ArgumentParser();ap.add_argument('base_laz',type=Path);ap.add_argument('base_brit',type=Path);ap.add_argument('base_od',type=Path);ap.add_argument('work',type=Path);ap.add_argument('repl',type=Path);ap.add_argument('--option-map',type=Path,required=True);ap.add_argument('--dynamic-map',type=Path,required=True);a=ap.parse_args()
    shutil.rmtree(a.work,ignore_errors=True);a.work.mkdir(parents=True)
    laz=a.work/'lazarus';br=a.work/'britannia';ko=a.work/'ondemand'
    shutil.copytree(a.base_laz,laz);shutil.copytree(a.base_brit,br);shutil.copytree(a.base_od,ko)
    os=patch_options(laz,br,ko,load_map(a.option_map));ds=patch_dynamic(laz,ko,load_map(a.dynamic_map));patch_system(laz,br)
    counts={'lazarus':make_replacements(a.base_laz,laz,a.repl/'lazarus'),'britannia':make_replacements(a.base_brit,br,a.repl/'britannia'),'ondemand':make_replacements(a.base_od,ko,a.repl/'ondemand')}
    print('OPTION',dict(os));print('DYNAMIC',dict(ds));print('REPLACEMENTS',counts)
    expected={'lazarus':267,'britannia':2,'ondemand':264}
    if counts!=expected:raise SystemExit(f'unexpected replacement counts: {counts} != {expected}')
if __name__=='__main__':main()
