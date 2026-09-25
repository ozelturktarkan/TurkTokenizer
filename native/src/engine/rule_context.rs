use std::io;
use crate::{rule_values::*,rule_data::*,rule_transition::*,lexicon::Lexeme,surface};
fn pb(c:&mut Ctx,k:&str,b:bool){put(c,k,Val::Bool(b));}
fn pv(c:&mut Ctx,k:&str,v:Option<char>){put(c,k,v.map_or(Val::Null,|v|Val::s(&v.to_string())));}
fn set(xs:Vec<String>)->Val{let mut xs=xs;xs.sort();xs.dedup();Val::Set(xs)}
fn add(c:&mut Ctx,k:&str,s:&str){let mut xs=match get(c,k){Some(Val::Set(xs))=>xs.clone(),_=>Vec::new()};xs.push(s.into());put(c,k,set(xs));}
fn inverse(v:Option<char>)->Option<char>{v.map(|v|match v{'a'=>'e','ı'=>'i','o'=>'ö','u'=>'ü',_=>v})}
fn has_suffix_vowel(n:&Node)->bool{n.ids.iter().any(|i|ROWS[*i].suffix().chars().any(vowel))}
// Only the fresh initializer uses these: all 26 field names are unique literals.
fn seed_value(c:&mut Ctx,k:&'static str,v:Val){c.push((std::borrow::Cow::Borrowed(k),v));}
fn seed_s(c:&mut Ctx,k:&'static str,v:&str){seed_value(c,k,Val::s(v));}
fn seed_b(c:&mut Ctx,k:&'static str,b:bool){seed_value(c,k,Val::Bool(b));}
fn seed_v(c:&mut Ctx,k:&'static str,v:Option<char>){seed_value(c,k,v.map_or(Val::Null,|v|Val::s(&v.to_string())));}
fn base(n:&Node,e:&Lexeme,r:&Row,mid:&str,s:&str,target:&str)->Ctx{
 let mut lv=surface::last_vowel(s);
 if has(e,"InverseHarmony")&&!has_suffix_vowel(n){lv=inverse(surface::last_vowel(&e.pronunciation));}
 if n.root()&&has(e,"LastVowelDrop")&&s!=e.stem{lv=surface::last_vowel(&e.pronunciation);}
 let mut pos=n.pos.as_str();
 if one(r.class,&["ksE","bfE"])||one(mid,&["CONV_KEN","COP_WHILE","TAM_IMP"]){pos="PREDICATE";}
 if one(r.id,&["ksE0072","ksE0073","ksE0074","ksE0075"]){pos="VERB";}
 if one(pos,&["ADJ","NUM"])&&one(r.class,&["clE","ylE","hlE","vtE"]){pos="NOMINALIZED";}
 if r.class=="ypE"&&r.licensed{pos="LEXICAL_BASE";}
 let intact=n.root();let par=if intact&&e.stem=="su"{"SU"}else if intact&&e.stem=="ne"{"NE"}else{"REGULAR"};
 let mut lexical=Vec::new();if n.phase=="V"{lexical.extend(["VOICE_PASS".into(),"VOICE_CAUS".into()]);}
 if one(&e.stem,&["gör","gül","vur","yaz","bak","kaç","uç","selamla"]){lexical.push("VOICE_RECIP".into());}
 if one(&e.stem,&["yıka","tara","giy","soy","öv"]){lexical.push("VOICE_REFL".into());}
 let last=ending(s);let nv=s.chars().filter(|c|vowel(*c)).count();
 let passive=if vowel(last)||last=='l'{"IN"}else{"IL"};
 let mut causative=if vowel(last)||"lr".contains(last)&&nv>1{"T"}else{"DIR"};
 for(a,v)in[("Causative_t","T"),("Causative_Ar","AR"),("Causative_Ir","IR"),("Causative_It","IT"),("Causative_At","AT")]{if n.root()&&has(e,a){causative=v;}}
 let aor=if vowel(last){"VOWEL_R"}else if if intact{has(e,"Aorist_I")}else{nv>1}{"I"}else{"A"};
 let mut zero=vec![if n.par.starts_with("IMP"){"AGR_2_SING"}else{"AGR_3_SING"}.into()];
 if n.phase=="V"{zero.push("TAM_IMP".into());}
 if one(&n.phase,&["N","NUM","POSS","CASE"]){zero.push("COP_PRESENT".into());}
 let after=s.chars().count()+r.suffix().chars().count();let following=target.chars().nth(after);
 let mut c=Vec::with_capacity(26);
 seed_s(&mut c,"surface_base",&n.surface);seed_s(&mut c,"pos",pos);seed_v(&mut c,"last_vowel",lv);seed_b(&mut c,"last_voiceless","fstkçşhp".contains(last));
 seed_s(&mut c,"last_segment",if vowel(last){"VOWEL"}else{"CONSONANT"});seed_s(&mut c,"lexeme",&e.lemma);
 seed_b(&mut c,"lexical_base_intact",intact);seed_value(&mut c,"lexical_license",set(lexical));seed_value(&mut c,"zero_transition_license",set(zero));
 seed_b(&mut c,"requires_pronominal_n",n.pos=="PRON"&&one(&e.stem,&["o","bu","şu"])||one(&n.poss,&["POSS_3_SING","POSS_3_PLUR"]));
 seed_s(&mut c,"possessive_paradigm",par);seed_s(&mut c,"genitive_paradigm",par);seed_s(&mut c,"nominal_number",&n.num);
 seed_b(&mut c,"relativizer_license",one(gs(&n.feats,"Case",""),&["Loc","Gen"])||intact&&one(&e.stem,&["dün","gün","bugün","yarın","şimdi","önce","sonra"]));
 seed_b(&mut c,"previous_is_multiverb",n.ids.iter().zip(n.mids.iter()).any(|(i,m)|m.starts_with("V_")&&ROWS[*i].class=="bvE"));
 seed_b(&mut c,"special_de_ye_stem",intact&&one(&e.stem,&["de","ye"]));seed_s(&mut c,"polarity",gs(&n.feats,"Polarity","Pos"));
 seed_s(&mut c,"passive_realization",passive);seed_s(&mut c,"causative_realization",causative);seed_s(&mut c,"aorist_paradigm",aor);
 seed_s(&mut c,"agreement_paradigm",if n.par=="NEG_AOR"&&mid=="AGR_1_PLUR"{"Z"}else{&n.par});seed_b(&mut c,"progressive_surface_ready","ıiuü".contains(last));
 seed_s(&mut c,"next_starts_with",match following{None=>"END",Some(c)if vowel(c)=>"VOWEL",_=>"CONSONANT"});
 seed_s(&mut c,"predicate_stage",if one(&n.phase,&["TAM","AGR"]){"TENSED_VERB"}else{"NOMINAL_PREDICATE"});
 seed_value(&mut c,"semantic_class",set(if intact&&one(&e.stem,&["saat","gün","hafta","ay","yıl","sene","dakika","saniye","zaman","asır","yüzyıl"]){vec!["TIME_OR_DURATION".into()]}else{Vec::new()}));
 seed_value(&mut c,"construction_license",set(Vec::new()));c
}
pub fn context(n:&Node,e:&Lexeme,r:&Row,mid:&str,s:&str,target:&str)->io::Result<Ctx>{
 if s.is_empty(){return Err(io::Error::other("context requires nonempty realized stem"));}
 let stem=if P1_CIRCUMFLEX{surface::phonetic(s)}else{s.into()};
 let local=nominal_stage(n);let mut c=base(&local,e,r,mid,&stem,target);
 // R2, then S05, then P1, P9, P10, in the frozen super-call order.
 if FLAGS.contains(&"ability_scope")&&mid=="TAM_AOR"&&n.last("ABILITY"){ps(&mut c,"polarity","Pos");}
 if FLAGS.contains(&"abbreviation")&&e.secondary=="Abbrv"&&n.root(){
  let pron=&e.pronunciation;
  if let Some(lv)=surface::last_vowel(pron){pv(&mut c,"last_vowel",Some(lv));ps(&mut c,"last_segment",if vowel(ending(pron)){"VOWEL"}else{"CONSONANT"});pb(&mut c,"last_voiceless","fstkçşhp".contains(ending(pron)));}
 }
 if mid=="CONV_REPEAT_A"&&ALLOW_REPEATED{put(&mut c,"construction_license",set(vec!["REPEATED_CONVERB".into()]));}
 if mid=="CONV_CASINA"&&as_if(n){put(&mut c,"construction_license",set(vec!["AS_IF".into()]));}
 if P1_PRONUNCIATION&&PRONUNCIATION_SOURCES.binary_search(&e.id.as_str()).is_ok()&&s.starts_with(&e.stem){
  let spoken=surface::phonetic(&format!("{}{}",e.pronunciation,&s[e.stem.len()..]));let mut lv=surface::last_vowel(&spoken);
  if has(e,"InverseHarmony")&&!has_suffix_vowel(n){lv=inverse(lv);}
  pv(&mut c,"last_vowel",lv);ps(&mut c,"last_segment",if vowel(ending(&spoken)){"VOWEL"}else{"CONSONANT"});pb(&mut c,"last_voiceless","fstkçşhp".contains(ending(&spoken)));
 }
 if e.pos=="PRON"&&one(&e.stem,&["o","bu","şu"])&&n.num=="Plur"&&n.poss.is_empty(){pb(&mut c,"requires_pronominal_n",false);}
 if n.root()&&e.pos=="VERB"{if let Some(v)=causative(&e.stem){ps(&mut c,"causative_realization",v);}}
 if n.root()&&n.phase=="N"&&(e.secondary=="Time"||one(&e.stem,&["ileri","geri","öte","beri"])){pb(&mut c,"relativizer_license",true);}
 if n.pos=="PRON"&&n.has("REL_KI_PRON")&&n.poss.is_empty(){pb(&mut c,"requires_pronominal_n",n.num!="Plur");}
 if n.root()&&e.pos=="VERB"&&RECIPROCALS.binary_search(&e.stem.as_str()).is_ok(){add(&mut c,"lexical_license","VOICE_RECIP");}
 if n.root()&&e.pos=="VERB"&&one(&e.stem,&["de","ye"])&&r.id=="ctE0022"{ps(&mut c,"passive_realization","NIL");}
 if n.phase=="V"&&n.mids.iter().any(|m|m.starts_with("VOICE_"))&&!vowel(ending(s)){ps(&mut c,"aorist_paradigm","I");}
 #[cfg(context_oracle)] {
  let original=crate::oracle_context::context(n,e,r,mid,s,target)?;
  crate::context_audit::check(&c,&original);
 }
 Ok(c)
}
pub fn phonology(pattern:&str,mut lv:char,mut vl:bool)->String{
 let mut out=String::new();for ch in pattern.chars(){
  let c=match ch{'A'=>if "eiöü".contains(lv){'e'}else{'a'},'I'=>match lv{'a'|'ı'=>'ı','e'|'i'=>'i','o'|'u'=>'u',_=>'ü'},'D'=>if vl{'t'}else{'d'},'C'=>if vl{'ç'}else{'c'},'G'=>if vl{'k'}else{'g'},_=>ch};
  out.push(c);if vowel(c){lv=c;}vl="fstkçşhp".contains(c);
 }out
}
fn test(c:&Cond,ctx:&Ctx)->io::Result<Option<bool>>{predicate(c.field,c.op,&c.value.value(),ctx)}
pub fn check_record(r:&Row,c:&Ctx,local:bool)->io::Result<Vec<String>>{
 let mut errors=Vec::new();
 if !r.enabled{errors.push("GENERATOR_DISABLED".into());}
 if !r.input.contains(&gs(c,"pos","\0")){errors.push("INPUT_POS".into());}
 if r.kind!="zero_morpheme"{
  if r.surface.is_none()||r.pattern.is_none(){errors.push("NO_REALIZATION".into());}
  else{
   let vowel_text=gs(c,"last_vowel","");let lv=vowel_text.chars().next();
   if vowel_text.chars().count()!=1||!lv.is_some_and(vowel)||get(c,"last_voiceless").is_none(){errors.push("UNKNOWN_PHONOLOGY".into());}
   else if phonology(r.pattern.unwrap(),lv.unwrap(),get(c,"last_voiceless").unwrap().truth())!=r.surface.unwrap(){errors.push("WRONG_ALLOMORPH".into());}
  }
 }
 for cond in r.left.iter().filter(|cond|!local||cond.field!="direct_agreement_target").chain(r.right.iter().filter(|cond|!local||!one(cond.field,&["next_morpheme","next_record"]))){
  match test(cond,c)?{Some(true)=>{},Some(false)=>errors.push(format!("CONSTRAINT:{}",cond.field)),None=>errors.push(format!("UNKNOWN:{}",cond.field))}
 }Ok(errors)
}
pub fn next_ok(n:&Node,r:&Row,mid:&str)->io::Result<bool>{
 if n.root(){return Ok(true);}
 let prev=&ROWS[*n.ids.last().unwrap()];let mut ctx=n.contexts.last().ok_or_else(||io::Error::other("next context missing"))?.clone();
 ps(&mut ctx,"next_record",r.id);ps(&mut ctx,"next_morpheme",mid);
 for cond in prev.right{if one(cond.field,&["next_morpheme","next_record"])&&test(cond,&ctx)?!=Some(true){return Ok(false);}}Ok(true)
}
pub fn final_ok(n:&Node)->io::Result<bool>{
 if one(&n.phase,&["COMPOUND_BASE","COMPOUND_NUM","QUESTION","NEGATIVE_COPULA","BOUND_POSS"]){return Ok(false);}
 let special=n.pos=="PART"||n.pos=="VERB"&&n.contexts.first().is_some_and(|c|hasstr(c,"lexeme","değil"));
 let cop=if special&&n.has("COP_PRESENT")&&hasstr(&n.feats,"Person","3")&&hasstr(&n.feats,"Number","Sing"){0}else{n.cop};
 if one(&n.phase,&["V","TAM","COP","BOUND"]){return Ok(false);}
 for (i,rid)in n.ids.iter().enumerate(){
  let r=&ROWS[*rid];let mut ctx=n.contexts.get(i).ok_or_else(||io::Error::other("final context missing"))?.clone();
  ps(&mut ctx,"next_record",n.ids.get(i+1).map_or("END",|j|ROWS[*j].id));ps(&mut ctx,"next_morpheme",n.mids.get(i+1).map_or("END",String::as_str));
  if r.left.iter().any(|c|c.field=="direct_agreement_target"){
   let direct=n.mids[i+1..].iter().find(|m|m.starts_with("AGR_")||m.starts_with("COP_"));
   let v=if let Some(m)=direct.filter(|m|m.starts_with("AGR_")){let bits:Vec<_>=m.split('_').collect();if bits.len()!=3{return Err(io::Error::other("direct agreement MID"));}format!("{}{}",bits[1],if bits[2]=="SING"{"Sing"}else{"Plur"})}else{"NONE".into()};
   ps(&mut ctx,"direct_agreement_target",&v);
  }
  for cond in r.left.iter().chain(r.right.iter()){if test(cond,&ctx)?!=Some(true){return Ok(false);}}
 }
 if cop!=0&&n.has("COP_PRESENT")&&hasstr(&n.feats,"Person","3")&&hasstr(&n.feats,"Number","Sing"){return Ok(false);}Ok(true)
}