use std::io::{self,Read,Write};
use std::fs::File;
use std::path::Path;
use std::borrow::Cow;
use crate::{wire::*,lexicon::Lexeme,tables::Table};
pub struct Config {flags:u32,compounds:Table,licenses:Table}
impl Config {
 pub fn open(dir:&Path)->io::Result<Self>{
  let mut f=File::open(dir.join("surface-flags.bin"))?;let mut magic=[0;8];f.read_exact(&mut magic)?;
  if &magic!=b"P77FLG1\0"{return Err(io::Error::other("surface flag magic"));}
  let flags=u32_in(&mut f)?;
  Ok(Self{flags,compounds:Table::open(&dir.join("compound-ids.bin"))?,licenses:Table::open(&dir.join("surface-licenses.bin"))?})
 }
 pub fn licensed(&mut self,rid:&str,base:&str,out:&str)->io::Result<bool>{Ok(self.licenses.get(&format!("{rid}\0{base}\0{out}"))?.is_some())}
}
#[derive(Clone,Debug)]
pub struct Node {pub surface:String,pub pos:String,pub phase:String,pub has_ids:bool,pub mids:Vec<String>}
pub struct Row<'a> {pub id:Cow<'a,str>,pub suffix:Cow<'a,str>,pub class:Cow<'a,str>,pub exact:bool,pub verb:bool}
fn bound<R:Read>(r:&mut R,max:u32)->io::Result<usize>{let n=u32_in(r)?;if n>max{return Err(io::Error::other("surface batch bound"));}Ok(n as usize)}
impl Node {
 fn read<R:Read>(r:&mut R)->io::Result<Self>{
  let surface=text_in(r)?;let pos=text_in(r)?;let phase=text_in(r)?;let has_ids=u32_in(r)?!=0;
  let n=bound(r,1024)?;let mut mids=Vec::new();for _ in 0..n{mids.push(text_in(r)?);}
  Ok(Self{surface,pos,phase,has_ids,mids})
 }
}
impl Row<'_> {
 fn read<R:Read>(r:&mut R)->io::Result<Self>{Ok(Self{id:text_in(r)?.into(),suffix:text_in(r)?.into(),class:text_in(r)?.into(),exact:u32_in(r)?!=0,verb:u32_in(r)?!=0})}
}
fn has(e:&Lexeme,a:&str)->bool{e.attrs.iter().any(|v|v==a)}
fn vowel(c:char)->bool{"aeıioöuü".contains(c)}
fn in_set(s:&str,xs:&[&str])->bool{xs.contains(&s)}
pub fn phonetic(raw:&str)->String{
 // Only an NFC-stable lowercase alphabet whose phonetic transform is identity.
 // Validate the ENTIRE string; a combining mark anywhere requires the old path.
 let identity=raw.chars().all(|c|match c{
  'ç'|'ğ'|'ı'|'ö'|'ş'|'ü'=>true,
  c=>c.is_ascii()&&!c.is_ascii_uppercase(),
 });
 let result=if identity{raw.to_owned()}else{
  crate::unicode::lower(raw).chars().map(|c|match c{'â'=>'a','î'=>'i','û'=>'u',_=>c}).collect()
 };
 #[cfg(phonetic_oracle)] crate::phonetic_audit::check_phonetic(raw,&result,identity);
 result
}
// Every accepted scalar is an NFC starter; no composition crosses these letters.
// If ANY scalar is outside this alphabet, retain full original Unicode behavior.
fn simple_last_vowel(raw:&str)->Option<Option<char>>{
 let mut last=None;
 for c in raw.chars(){
  let v=match c{
   'a'|'A'|'â'|'Â'=>Some('a'),'e'|'E'=>Some('e'),
   'ı'|'I'=>Some('ı'),'i'|'İ'|'î'|'Î'=>Some('i'),
   'o'|'O'=>Some('o'),'ö'|'Ö'=>Some('ö'),
   'u'|'U'|'û'|'Û'=>Some('u'),'ü'|'Ü'=>Some('ü'),
   'ç'|'Ç'|'ğ'|'Ğ'|'ş'|'Ş'=>None,
   c if c.is_ascii()=>None,
   _=>return None,
  };
  if v.is_some(){last=v;}
 }
 Some(last)
}
pub fn last_vowel(raw:&str)->Option<char>{
 let simple=simple_last_vowel(raw);
 let result=simple.unwrap_or_else(||phonetic(raw).chars().rev().find(|&c|vowel(c)));
 #[cfg(phonetic_oracle)] crate::phonetic_audit::check(raw,result,simple.is_some());
 result
}
pub fn harmonic(raw:&str)->Option<char>{last_vowel(raw).map(|c|match c{'a'|'ı'=>'ı','e'|'i'=>'i','o'|'u'=>'u',_=>'ü'})}
fn harmonic_required(raw:&str)->io::Result<char>{harmonic(raw).ok_or_else(||io::Error::other("harmonic_i requires a vowel"))}
fn one_mid(n:&Node,mid:&str)->bool{n.mids.len()==1 && n.mids[0]==mid}
fn nominal(pos:&str)->bool{in_set(pos,&["NOUN","PROPN","PRON","NOMINALIZED","ADJ","NUM"])}
pub fn initial(cfg:&mut Config,e:&Lexeme)->io::Result<(Node,Vec<(&'static str,&'static str)>,&'static str)>{
 let mut phase=if e.pos=="LEXICAL_BASE"{"BOUND"}else if e.pos=="VERB"{"V"}else if nominal(&e.pos){"N"}else{"END"};
 let mut feats=Vec::new();let mut poss="";
 if has(e,"R1Question"){phase="QUESTION";}
 else if has(e,"R1NegativeCopula"){phase="NEGATIVE_COPULA";feats.push(("Polarity","Neg"));}
 else if has(e,"R1BoundPossessiveRoot"){phase="BOUND_POSS";}
 else if cfg.flags&1!=0 && e.pos=="ADP"{phase="POSTPOSITION";}
 if has(e,"P9CompoundStem"){phase="COMPOUND_BASE";}
 else if cfg.compounds.get(&e.id)?.is_some(){phase="POSS";poss="POSS_3_SING";feats=vec![("Number[psor]","Sing"),("Person[psor]","3")];}
 Ok((Node{surface:e.stem.clone(),pos:e.pos.clone(),phase:phase.into(),has_ids:false,mids:Vec::new()},feats,poss))
}
pub fn classes(n:&Node,e:&Lexeme)->Vec<&'static str>{
 if n.phase=="COMPOUND_BASE"{return vec!["clE","ylE"];}
 if n.phase=="COMPOUND_NUM"{return vec!["ylE"];}
 let mut out=match n.phase.as_str(){
  "QUESTION"|"NEGATIVE_COPULA"|"POSTPOSITION"=>vec!["bfE"],"BOUND_POSS"=>vec!["ylE"],
  "BOUND"=>vec!["ypE"],"V"=>vec!["ctE","ybE","olE","bvE","ffE","fiE","fsE","flE","zmE"],
  "TAM"=>vec!["ksE","bfE","flE"],"AGR"=>vec!["bfE"],"COP"=>vec!["ksE"],"END"=>vec![],
  phase=>{
   let mut v=vec!["bfE","flE"];
   if in_set(phase,&["N","NUM","POSS"]){v.extend(["hlE","vtE"]);}
   if in_set(phase,&["N","NUM"]){v.push("ylE");}
   if phase=="N"{v.extend(["clE","ffE","fiE","fsE","ifE","iiE","isE","kcE","sdE","sfE","siE","syE","ypE","zyE"]);}
   if phase=="CASE" || (phase=="N"&&in_set(&e.stem,&["dün","gün","bugün","yarın","şimdi","önce","sonra"])){v.push("atE");}
   v
  }
 };
 if !n.has_ids && e.lemma=="az" && e.pos=="ADV"{out.push("kcE");}
 if n.pos=="VERB"&&n.phase=="AGR"&&n.mids.len()>=2&&n.mids[n.mids.len()-1]=="AGR_3_SING"&&in_set(&n.mids[n.mids.len()-2],&["TAM_AOR","TAM_EVID"]){out.push("flE");}
 let mut seen=Vec::new();out.retain(|x|if seen.contains(x){false}else{seen.push(*x);true});
 if !n.has_ids&&n.phase=="N"&&(e.secondary=="Time"||in_set(&e.stem,&["ileri","geri","öte","beri"]))&&!out.contains(&"atE"){out.push("atE");}
 out
}
pub fn changed(cfg:&mut Config,n:&Node,e:&Lexeme,r:&Row,mid:&str)->io::Result<(String,Vec<&'static str>)>{
 if one_mid(n,"TAM_IMP")&&e.stem=="ye"&&e.pos=="VERB"&&mid=="AGR_2_PLUR"{return Ok(("yi".into(),vec!["diR0001"]));}
 let mut root=!n.has_ids;let mut mids=n.mids.as_slice();
 if one_mid(n,"COP_PRESENT")&&n.surface==e.stem&&e.pos!="VERB"&&r.suffix.chars().next().is_some_and(vowel){root=true;mids=&[];}
 else if root&&mid=="DIM_CIK"{
  let fixed=match (e.lemma.as_str(),e.pos.as_str()){("dar","ADJ")=>Some("dara"),("genç","ADJ")=>Some("gence"),("az","ADV")=>Some("azı"),("bir","NUM")=>Some("biri"),_=>None};
  if let Some(s)=fixed{return Ok((s.into(),vec!["hdR0001"]));}
 }else if root&&in_set(mid,&["CONV_REPEAT_A","TAM_OPT"])&&e.pos=="VERB"&&in_set(&e.stem,&["de","ye"]){
  return Ok((format!("{}i",e.stem.chars().next().unwrap()),vec!["diR0001"]));
 }
 if cfg.flags&2!=0 && mids.len()==1&&mids[0]=="TAM_IMP"&&mid=="AGR_2_PLUR"&&has(e,"Voicing"){root=true;mids=&[];}
 let mut s=n.surface.clone();let mut trace=Vec::new();
 if r.exact&&cfg.licensed(&r.id,&s,&format!("{s}{}",r.suffix))?{return Ok((s,trace));}
 if root {
  if e.pos=="PRON"&&in_set(&e.stem,&["ben","sen"])&&mid=="CASE_DAT"{s=format!("{}an",e.stem.chars().next().unwrap());trace.push("zaR0001");}
  if e.pos=="PRON"&&in_set(&e.stem,&["o","bu","şu"])&&mid=="NUMBER_PL"{s=format!("{}n",e.stem);trace.push("PRONOMINAL_PLURAL_STEM");}
  if e.pos=="VERB"&&in_set(&e.stem,&["de","ye"])&&
   (in_set(mid,&["TAM_FUT","PART_FUT","PART_AN","CONV_ARAK","ABILITY","ABILITY_NEG_BASE","TAM_PROG1"]) || e.stem=="ye"&&mid=="CONV_IP"){
   s=format!("{}i",e.stem.chars().next().unwrap());trace.push("diR0001");
  }
  if mid=="DIM_CIK"&&in_set(&e.stem,&["küçük","minik"]){s=e.stem.clone();s.pop();trace.push("hdR0001");}
  if e.pos=="VERB"&&mid=="TAM_PROG1"&&e.stem.chars().last().is_some_and(vowel)&&!in_set(&e.stem,&["de","ye"]){
   let mut base=e.stem.clone();base.pop();let v=harmonic_required(if last_vowel(&base).is_some(){&base}else{&e.stem})?;
   base.push(v);s=base;trace.push("uyR0001");
  }
  if r.suffix.chars().next().is_some_and(vowel)&&s==e.stem {
   let mut chars:Vec<char>=s.chars().collect();
   if has(e,"LastVowelDrop")&&chars.len()>2&&vowel(chars[chars.len()-2])&&in_set(&r.class,&["hlE","ylE","ctE"]){chars.remove(chars.len()-2);trace.push("udR0001");}
   if has(e,"Voicing")&&chars.last().is_some_and(|&c|"pçtkg".contains(c))&&mid!="TAM_PAST"{
    let next=match *chars.last().unwrap(){'p'=>'b','ç'=>'c','t'=>'d','k'=>if chars.ends_with(&['n','k']){'g'}else{'ğ'},_=>'ğ'};
    *chars.last_mut().unwrap()=next;trace.push("unR0004");
   }
   if has(e,"Doubling")&&in_set(&r.class,&["hlE","ylE"]){let last=*chars.last().ok_or_else(||io::Error::other("empty doubling stem"))?;chars.push(last);trace.push("uzR0001");}
   s=chars.into_iter().collect();
  }
 }else if mid=="TAM_PROG1"&&n.phase=="V"&&s.ends_with(['a','e'])&&mids.last().is_some_and(|m|m!="POLARITY_NEG"){
  let mut base=s.clone();base.pop();let v=harmonic_required(if last_vowel(&base).is_some(){&base}else{&s})?;base.push(v);s=base;trace.push("uyR0001");
 }
 Ok((s,trace))
}
pub fn prefix(cfg:&Config,n:&Node,e:&Lexeme,r:&Row,mid:&str,surface:&str,target:&str)->io::Result<bool>{
 if target.starts_with(surface){return Ok(true);}
 let variants=||->io::Result<bool>{let len=e.stem.chars().count();Ok(crate::lexicon::variants(e)?.iter().any(|v|v.chars().count()==len&&target.starts_with(v)))};
 if cfg.flags&2!=0&&!n.has_ids&&e.pos=="VERB"&&has(e,"Voicing")&&mid=="TAM_IMP"&&r.suffix.is_empty()&&variants()?{return Ok(true);}
 if !n.has_ids&&mid=="COP_PRESENT"&&has(e,"Voicing")&&variants()?{return Ok(true);}
 if !n.has_ids&&mid=="TAM_IMP"&&e.stem=="ye"&&e.pos=="VERB"&&target.starts_with("yi"){return Ok(true);}
 if r.verb&&surface.ends_with(['a','e']){
  let mut base=surface.to_owned();base.pop();
  if let Some(v)=harmonic(&base){base.push(v);base.push_str("yor");if target.starts_with(&base){return Ok(true);}}
 }
 Ok(false)
}
fn strings_out<W:Write>(w:&mut W,ss:&[&str])->io::Result<()>{u32_out(w,ss.len()as u32)?;for s in ss{text_out(w,s)?;}Ok(())}
pub fn command<R:Read,W:Write>(cmd:u32,r:&mut R,w:&mut W,cfg:&mut Config)->io::Result<()>{
 match cmd {
  24=>{
   let n=bound(r,128)?;let mut es=Vec::new();for _ in 0..n{es.push(Lexeme::read(r)?);}
   for e in es{
    let (node,feats,poss)=initial(cfg,&e)?;
    for s in [&node.surface,&node.pos,&node.phase]{text_out(w,s)?;}
    u32_out(w,feats.len()as u32)?;for(k,v)in feats{text_out(w,k)?;text_out(w,v)?;}
    text_out(w,"")?;text_out(w,"Sing")?;text_out(w,poss)?;u32_out(w,0)?;u32_out(w,0)?;
    strings_out(w,&classes(&node,&e))?;
   }
  },
  25=>{
   let count=bound(r,128)?;let mut xs=Vec::new();for _ in 0..count{xs.push((Node::read(r)?,Lexeme::read(r)?));}
   for (n,e) in xs{strings_out(w,&classes(&n,&e))?;}
  },
  26=>{
   let n=Node::read(r)?;let e=Lexeme::read(r)?;let target=text_in(r)?;let count=bound(r,32)?;let mut xs=Vec::new();
   for _ in 0..count{let row=Row::read(r)?;let mid=text_in(r)?;let num=bound(r,32)?;let mut outputs=Vec::new();for _ in 0..num{outputs.push((text_in(r)?,text_in(r)?));}xs.push((row,mid,outputs));}
   for (row,mid,outputs) in xs{
    let (stem,trace)=changed(cfg,&n,&e,&row,&mid)?;let surface=format!("{stem}{}",row.suffix);let ok=prefix(cfg,&n,&e,&row,&mid,&surface,&target)?;
    text_out(w,&stem)?;strings_out(w,&trace)?;u32_out(w,ok as u32)?;
    if ok {for(pos,phase)in outputs{let mut next=n.clone();next.surface=surface.clone();next.pos=pos;next.phase=phase;next.has_ids=true;next.mids.push(mid.clone());strings_out(w,&classes(&next,&e))?;}}
   }
  },
  27=>{
   let count=bound(r,128)?;let mut xs=Vec::new();for _ in 0..count{xs.push(text_in(r)?);}
   for s in xs{text_out(w,&phonetic(&s))?;u32_out(w,last_vowel(&s).map_or(u32::MAX,|c|c as u32))?;u32_out(w,harmonic(&s).map_or(u32::MAX,|c|c as u32))?;}
  },
  28=>{
   let count=bound(r,128)?;let mut xs=Vec::new();for _ in 0..count{xs.push((Node::read(r)?,Lexeme::read(r)?,Row::read(r)?,text_in(r)?,text_in(r)?,text_in(r)?));}
   for(n,e,row,mid,surface,target)in xs{u32_out(w,prefix(cfg,&n,&e,&row,&mid,&surface,&target)?as u32)?;}
  },
  _=>return Err(io::Error::other("surface command"))
 }w.flush()
}