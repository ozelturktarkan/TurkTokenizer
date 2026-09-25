use std::{io,borrow::Cow};
use crate::{rule_values::*,rule_data::*,lexicon::{Lexeme,Store}};
pub fn one(s:&str,x:&[&str])->bool{x.contains(&s)}
pub fn vowel(c:char)->bool{"aeıioöuü".contains(c)}
pub fn ending(s:&str)->char{s.chars().last().unwrap_or('\0')}
pub fn has(e:&Lexeme,a:&str)->bool{e.attrs.iter().any(|x|x==a)}
pub fn gs<'a>(c:&'a Ctx,k:&str,d:&'a str)->&'a str{if let Some(Val::Str(s))=get(c,k){s}else{d}}
pub fn ps(c:&mut Ctx,k:&str,v:&str){put(c,k,Val::s(v));}
fn title(s:&str)->String{let mut b=s.to_ascii_lowercase().into_bytes();if let Some(c)=b.first_mut(){c.make_ascii_uppercase();}String::from_utf8(b).unwrap()}
fn nominal(s:&str)->bool{one(s,&["NOUN","PROPN","PRON","NOMINALIZED","ADJ","NUM"])}
fn convert(s:&str)->bool{one(s,&["ADJ","NUM"])}
fn neg_converb(s:&str)->bool{one(s,&["CONV_MADAN","CONV_MAKSIZIN"])}
fn voice(s:&str)->Option<&'static str>{match s{"VOICE_CAUS"=>Some("Cau"),"VOICE_PASS"=>Some("Pass"),"VOICE_RECIP"=>Some("Rcp"),"VOICE_REFL"=>Some("Rfl"),_=>None}}
pub fn as_if(n:&Node)->bool{n.pos=="VERB"&&n.phase=="AGR"&&n.mids.len()>=2&&n.last("AGR_3_SING")&&one(&n.mids[n.mids.len()-2],&["TAM_AOR","TAM_EVID"])}
pub fn nominal_stage(n:&Node)->Cow<'_,Node>{if one(&n.phase,&["QUESTION","NEGATIVE_COPULA","POSTPOSITION","BOUND_POSS"]){let mut nn=n.clone();nn.phase="N".into();Cow::Owned(nn)}else{Cow::Borrowed(n)}}
fn fresh(n:&Node,pos:&str,phase:&str,feats:Ctx,par:&str,num:&str,poss:&str,deriv:u32)->Out{
 Out{pos:pos.into(),phase:phase.into(),feats,par:par.into(),num:num.into(),poss:poss.into(),cop:n.cop,deriv}
}
fn fs(pairs:&[(&'static str,&str)])->Ctx{
 #[cfg(transition_keys)]{crate::transition_keys::fields(pairs)}
 #[cfg(not(transition_keys))]{pairs.iter().map(|(k,v)|(k.to_string().into(),Val::s(v))).collect()}
}

// A rejected transition need not clone every field of its input node.
// Each modified field becomes owned explicitly; accepted output owns all data.
struct View<'a>{pos:Cow<'a,str>,phase:Cow<'a,str>,feats:Cow<'a,Ctx>,par:Cow<'a,str>,num:Cow<'a,str>,poss:Cow<'a,str>,cop:u32,deriv:u32}
impl<'a> View<'a>{
 fn new(n:&'a Node)->Self{Self{pos:Cow::Borrowed(&n.pos),phase:Cow::Borrowed(&n.phase),feats:Cow::Borrowed(&n.feats),par:Cow::Borrowed(&n.par),num:Cow::Borrowed(&n.num),poss:Cow::Borrowed(&n.poss),cop:n.cop,deriv:n.deriv}}
 fn into_out(self)->Out{Out{pos:self.pos.into_owned(),phase:self.phase.into_owned(),feats:self.feats.into_owned(),par:self.par.into_owned(),num:self.num.into_owned(),poss:self.poss.into_owned(),cop:self.cop,deriv:self.deriv}}
}
fn base(n:&Node,e:&Lexeme,r:&Row,mid:&str,lex:&mut Store)->io::Result<Option<Vec<Out>>>{
 let mut o=View::new(n);let cls=r.class;
 if mid=="NUMBER_PL"{
  if !nominal(&o.pos)||o.phase!="N"{return Ok(None);}
  if convert(&o.pos){o.pos="NOMINALIZED".into();}o.phase="NUM".into();o.num="Plur".into();crate::p119_ps!(o.feats.to_mut(),"Number","Plur");
 }else if mid.starts_with("POSS_"){
  if !nominal(&o.pos)||!one(&o.phase,&["N","NUM"]){return Ok(None);}
  if convert(&o.pos){o.pos="NOMINALIZED".into();}o.phase="POSS".into();o.poss=mid.into();
  let bits:Vec<_>=mid.split('_').collect();if bits.len()!=3{return Err(io::Error::other("possessive MID shape"));}
  crate::p119_ps!(o.feats.to_mut(),"Person[psor]",bits[1]);crate::p119_ps!(o.feats.to_mut(),"Number[psor]",&title(bits[2]));
 }else if mid.starts_with("CASE_"){
  if !nominal(&o.pos)||!one(&o.phase,&["N","NUM","POSS"]){return Ok(None);}
  if convert(&o.pos){o.pos="NOMINALIZED".into();}o.phase="CASE".into();crate::p119_ps!(o.feats.to_mut(),"Case",&title(&mid[5..]));
 }else if cls=="atE"{
  o.pos=if mid=="REL_KI_ADJ"{"ADJ"}else{"PRON"}.into();o.phase="N".into();o.feats.to_mut().clear();o.num="Sing".into();o.poss.to_mut().clear();o.deriv+=1;
 }else if cls=="ctE"{
  if o.phase!="V"||["POLARITY_NEG","ABILITY","ABILITY_NEG_BASE"].iter().any(|m|n.has(m)){return Ok(None);}
  if one(mid,&["VOICE_PASS","VOICE_RECIP","VOICE_REFL"])&&n.has(mid){return Ok(None);}
  if n.has("VOICE_PASS"){return Ok(None);}
  let v=voice(mid).ok_or_else(||io::Error::other("voice MID"))?;crate::p119_ps!(o.feats.to_mut(),"Voice",v);o.deriv+=1;
 }else if mid=="POLARITY_NEG"{
  if o.phase!="V"||n.last("POLARITY_NEG"){return Ok(None);}crate::p119_ps!(o.feats.to_mut(),"Polarity","Neg");
 }else if cls=="ybE"{
  if o.phase!="V"||n.has("ABILITY")||n.has("ABILITY_NEG_BASE"){return Ok(None);}
  if !r.suffix().is_empty()&&!r.suffix().starts_with('y')&&vowel(ending(&n.surface)){return Ok(None);}
  crate::p119_ps!(o.feats.to_mut(),"Mood","Pot");o.deriv+=1;
 }else if cls=="bvE"{
  if o.phase!="V"||n.ids.iter().any(|i|ROWS[*i].class=="bvE"){return Ok(None);}o.deriv+=1;
 }else if cls=="zmE"{
  if o.phase!="V"{return Ok(None);}let neg=hasstr(&o.feats,"Polarity","Neg");
  if mid=="TAM_AOR"&&(one(r.id,&["zmE0043","zmE0044"])!=neg){return Ok(None);}
  let mood=match mid{"TAM_IMP"=>"Imp","TAM_COND"=>"Cnd","TAM_OPT"=>"Opt","TAM_NEC"=>"Nec",_=>gs(&o.feats,"Mood","Ind")}.to_owned();
  crate::p119_ps!(o.feats.to_mut(),"VerbForm","Fin");crate::p119_ps!(o.feats.to_mut(),"Mood",&mood);
  crate::p119_ps!(o.feats.to_mut(),"Tense",if one(mid,&["TAM_PAST","TAM_EVID"]){"Past"}else if mid=="TAM_FUT"{"Fut"}else{"Pres"});
  if mid=="TAM_EVID"{crate::p119_ps!(o.feats.to_mut(),"Evident","Nfh");}
  if one(mid,&["TAM_PROG1","TAM_PROG2"]){crate::p119_ps!(o.feats.to_mut(),"Aspect","Prog");}
  if mid=="TAM_AOR"{crate::p119_ps!(o.feats.to_mut(),"Aspect","Hab");}
  o.phase="TAM".into();o.par=if one(mid,&["TAM_PAST","TAM_COND"]){"K"}else if mid=="TAM_IMP"{"IMP"}else if mid=="TAM_OPT"{"OPT"}else if r.id=="zmE0044"{"NEG_AOR"}else{"Z"}.into();
 }else if cls=="ksE"{
  if !one(&o.phase,&["TAM","COP"]){return Ok(None);}
  if o.par=="IMP"&&r.id=="ksE0000"||o.par!="IMP"&&r.id=="ksE0036"{return Ok(None);}
  if mid=="AGR_3_PLUR"&&n.num=="Plur"&&n.last("COP_PRESENT"){return Ok(None);}
  if o.par.starts_with("IMP")&&!r.suffix().is_empty()&&!one(r.id,&["ksE0072","ksE0073","ksE0074","ksE0075"])&&mid=="AGR_2_PLUR"{
   if r.suffix().starts_with('y')!=vowel(ending(&n.surface)){return Ok(None);}
  }
  let bits:Vec<_>=mid.split('_').collect();if bits.len()!=3{return Err(io::Error::other("agreement MID shape"));}
  crate::p119_ps!(o.feats.to_mut(),"Person",bits[1]);crate::p119_ps!(o.feats.to_mut(),"Number",&title(bits[2]));o.phase="AGR".into();
 }else if cls=="bfE"{
  if mid=="COP_WHILE"{
   if !one(&o.phase,&["N","NUM","POSS","CASE","TAM"])||n.par=="IMP"{return Ok(None);}
   return Ok(Some(vec![fresh(n,"ADV","END",fs(&[("VerbForm","Conv")]),&o.par,&o.num,&o.poss,o.deriv)]));
  }
  if o.cop>=1||!one(&o.phase,&["N","NUM","POSS","CASE","TAM","AGR"]){return Ok(None);}
  let pre=o.phase=="AGR"&&hasstr(&o.feats,"Person","3")&&hasstr(&o.feats,"Number","Plur")&&one(mid,&["COP_PAST","COP_EVID","COP_COND"]);
  if o.phase=="AGR"&&mid!="COP_GENERAL"&&!pre{return Ok(None);}
  if one(&o.phase,&["TAM","AGR"])&&n.par=="IMP"||mid=="COP_PRESENT"&&one(&o.phase,&["TAM","AGR"]){return Ok(None);}
  o.cop+=1;o.phase="COP".into();o.par=if one(mid,&["COP_PAST","COP_COND"]){"K"}else{"Z"}.into();
  let tense=if one(mid,&["COP_PAST","COP_EVID"]){"Past"}else{gs(&o.feats,"Tense","Pres")}.to_owned();
  crate::p119_ps!(o.feats.to_mut(),"VerbForm","Fin");crate::p119_ps!(o.feats.to_mut(),"Mood",if mid=="COP_COND"{"Cnd"}else{"Ind"});crate::p119_ps!(o.feats.to_mut(),"Tense",&tense);
  if mid=="COP_EVID"{crate::p119_ps!(o.feats.to_mut(),"Evident","Nfh");}
  if n.phase=="AGR"&&(mid=="COP_GENERAL"||pre){o.phase="AGR".into();}
 }else if cls=="flE"{
  if mid=="CONV_KEN"{if !one(&o.phase,&["TAM","N","NUM","POSS","CASE"])||n.par=="IMP"{return Ok(None);}}
  else if o.phase!="V"{return Ok(None);}
  if neg_converb(mid)&&hasstr(&o.feats,"Polarity","Neg"){return Ok(None);}
  if mid=="PART_AOR"&&((r.surface==Some("z"))!=hasstr(&o.feats,"Polarity","Neg")){return Ok(None);}
  if mid.starts_with("CONV_"){
   return Ok(Some(vec![fresh(n,"ADV","END",fs(&[("VerbForm","Conv"),("Polarity",if neg_converb(mid){"Neg"}else{gs(&o.feats,"Polarity","Pos")})]),&o.par,&o.num,&o.poss,o.deriv+1)]));
  }
  if mid.starts_with("PART_"){
   crate::p119_ps!(o.feats.to_mut(),"VerbForm","Part");return Ok(Some(vec![fresh(n,"ADJ","N",o.feats.as_ref().clone(),&o.par,"Sing","",o.deriv+1),fresh(n,"NOMINALIZED","N",o.feats.into_owned(),&o.par,"Sing","",o.deriv+1)]));
  }
  return Ok(Some(vec![fresh(n,"NOMINALIZED","N",fs(&[("VerbForm","Vnoun")]),&o.par,"Sing","",o.deriv+1)]));
 }else if one(cls,&["ffE","fiE","fsE","ifE","iiE","isE","kcE","sdE","sfE","siE","ypE","zyE","syE"]){
  if !one(&o.phase,&["N","V","BOUND"]){return Ok(None);}
  if one(cls,&["ffE","fiE","fsE"])&&(o.phase!="V"||hasstr(&o.feats,"Polarity","Neg")){return Ok(None);}
  if !one(cls,&["ffE","fiE","fsE"])&&o.phase!="N"&&!(o.phase=="BOUND"&&cls=="ypE"){return Ok(None);}
  let mut result=Vec::new();
  for out in r.output{
   if !one(out,&["VERB","NOUN","NOMINALIZED","ADJ","ADV","NUM","PRON","PROPN"])||cls=="kcE"&&*out!=o.pos{continue;}
   if r.exact()&&r.output.len()>1{
    let attested=lex.by_stem(&format!("{}{}",n.surface,r.suffix()))?;
    if !attested.is_empty()&&!attested.iter().any(|e|e.pos==*out){continue;}
   }
   result.push(fresh(n,out,if *out=="VERB"{"V"}else if *out=="ADV"{"END"}else{"N"},Vec::new(),"","Sing","",o.deriv+1));
  }
  return Ok(Some(result));
 }else{return Ok(None);}
 let _=e;Ok(Some(vec![o.into_out()]))
}
fn r1(n:&Node,e:&Lexeme,r:&Row,mid:&str,lex:&mut Store)->io::Result<Option<Vec<Out>>>{
 let mut out=base(n,e,r,mid,lex)?;
 if r.class=="flE"||r.class=="bfE"&&mid=="COP_WHILE"{
  if let Some(xs)=out.as_mut(){for x in xs{if one(gs(&x.feats,"VerbForm",""),&["Vnoun","Conv"]){
   for key in ["Polarity","Voice"]{if let Some(v)=get(&n.feats,key){crate::p119_put!(&mut x.feats,key,v.clone());}}
   if neg_converb(mid){crate::p119_ps!(&mut x.feats,"Polarity","Neg");}
  }}}
 }Ok(out)
}
fn r2(n:&Node,e:&Lexeme,r:&Row,mid:&str,lex:&mut Store)->io::Result<Option<Vec<Out>>>{
 let mut local=nominal_stage(n);let ability=FLAGS.contains(&"ability_scope");
 if ability&&mid=="ABILITY"&&n.phase=="V"&&n.last("POLARITY_NEG"){local.to_mut().mids.retain(|x|!one(x,&["ABILITY","ABILITY_NEG_BASE"]));}
 let restore=ability&&mid=="TAM_AOR"&&n.last("ABILITY")&&hasstr(&n.feats,"Polarity","Neg");
 if restore{crate::p119_ps!(&mut local.to_mut().feats,"Polarity","Pos");local.to_mut().feats.sort_by(|a,b|a.0.cmp(&b.0));}
 let mut out=r1(&local,e,r,mid,lex)?;if restore{if let Some(xs)=out.as_mut(){for x in xs{crate::p119_ps!(&mut x.feats,"Polarity","Neg");}}}Ok(out)
}
fn s02(n:&Node,e:&Lexeme,r:&Row,mid:&str,lex:&mut Store)->io::Result<Option<Vec<Out>>>{
 let mut out=r2(n,e,r,mid,lex)?;
 if n.pos=="ADJ"&&n.phase=="N"&&hasstr(&n.feats,"VerbForm","Part")&&mid.starts_with("POSS_")&&(n.last("PART_DIK")||n.last("PART_FUT")){
  if let Some(xs)=out.as_mut(){let extra:Vec<_>=xs.iter().map(|x|{let mut y=x.clone();y.pos="ADJ".into();y}).collect();xs.extend(extra);}
 }Ok(out)
}
fn s05(n:&Node,e:&Lexeme,r:&Row,mid:&str,lex:&mut Store)->io::Result<Option<Vec<Out>>>{
 let mut out=if mid=="CONV_CASINA"{
  if !as_if(n){return Ok(None);}
  let mut f=fs(&[("VerbForm","Conv"),("Polarity",gs(&n.feats,"Polarity","Pos"))]);if let Some(v)=get(&n.feats,"Voice"){crate::p119_put!(&mut f,"Voice",v.clone());}
  Some(vec![fresh(n,"ADV","END",f,&n.par,&n.num,&n.poss,n.deriv+1)])
 }else if r.handler=="S05_BIR_DIMINUTIVE"{
  if !n.root()||e.lemma!="bir"||e.pos!="NUM"||n.phase!="N"{return Ok(None);}
  Some(vec![fresh(n,"ADJ","N",Vec::new(),"","Sing","",n.deriv+1)])
 }else{
  let mut local=Cow::Borrowed(n);
  if n.root()&&mid=="DIM_CIK"&&e.lemma=="az"&&e.pos=="ADV"{local.to_mut().phase="N".into();}
  s02(&local,e,r,mid,lex)?
 };
 if let Some(xs)=out.as_mut(){
  let chain:Vec<_>=n.mids.iter().map(String::as_str).chain(std::iter::once(mid)).filter_map(voice).collect();
  if chain.len()>1{let chain=chain.join(",");for x in xs{if get(&x.feats,"Voice").is_some(){crate::p119_ps!(&mut x.feats,"VoiceChain",&chain);}}}
 }Ok(out)
}
fn g9(n:&Node,e:&Lexeme,r:&Row,mid:&str,lex:&mut Store)->io::Result<Option<Vec<Out>>>{
 if !r.license.is_empty(){
  if e.pos!="PRON"||!r.roots.contains(&e.stem.as_str()){return Ok(None);}
  if r.license=="PRON_ROOT"&&!n.root(){return Ok(None);}
  if r.license=="PRON_ZERO"{if mid=="POSS_3_PLUR"{if n.mids!=["NUMBER_PL"]{return Ok(None);}}else if !n.root(){return Ok(None);}}
 }
 if e.pos=="PRON"&&n.root(){
  if one(&e.stem,&["ben","sen","o","biz","siz","bu","şu"])&&mid.starts_with("POSS_"){return Ok(None);}
  if one(&e.stem,&["ben","biz"])&&mid=="CASE_GEN"&&r.id!="P9:hlE:pron:im"{return Ok(None);}
  if one(&e.stem,&["o","bu","şu"])&&mid=="CASE_INS"&&r.license.is_empty(){return Ok(None);}
 }s05(n,e,r,mid,lex)
}
fn g21(n:&Node,e:&Lexeme,r:&Row,mid:&str,lex:&mut Store)->io::Result<Option<Vec<Out>>>{
 if !r.family.is_empty(){
  if n.pos!="ADJ"||n.phase!="N"{return Ok(None);}
  if r.family=="asif"{
   if n.mids.iter().any(|m|one(m,&["CONV_CASINA","DERIV_MANNER_CA","N_AGENT","A_AGENT","V_AGENT","V_INHERENT","WITH","SIMILAR"])){return Ok(None);}
   return Ok(Some(vec![fresh(n,"ADJ","N",Vec::new(),"","Sing","",n.deriv+1)]));
  }
 }g9(n,e,r,mid,lex)
}
pub fn transition(n:&Node,e:&Lexeme,r:&Row,mid:&str,lex:&mut Store)->io::Result<Option<Vec<Out>>>{
 let mut local=Cow::Borrowed(n);let compound=one(&n.phase,&["COMPOUND_BASE","COMPOUND_NUM"]);
 if compound{local.to_mut().phase=if n.phase=="COMPOUND_BASE"{"N"}else{"NUM"}.into();}
 let mut out=g21(&local,e,r,mid,lex)?;
 if compound&&mid=="NUMBER_PL"{if let Some(xs)=out.as_mut(){for x in xs{x.phase="COMPOUND_NUM".into();}}}Ok(out)
}