//! Necessary condition for the unchanged surface::prefix predicate.
//! A true result only permits the original rule checks; it does not accept a path.
use std::cell::Cell;
use crate::rule_data::{Row,ROWS};
thread_local! {static COUNTS:Cell<[u64;2]>=const{Cell::new([0;2])};}
pub fn info()->[u64;2]{COUNTS.with(Cell::get)}
pub fn reset(){COUNTS.with(|c|c.set([0;2]));}
pub(crate) fn record(skipped:u64,checked:u64){COUNTS.with(|c|{let x=c.get();c.set([x[0]+skipped,x[1]+checked]);});}
fn possible(r:&Row,target:&str)->bool{
 let suffix=r.suffix();
 // Root variants and ye/yi may be accepted independently of the full surface.
 if suffix.is_empty()||r.mids.contains(&"TAM_IMP")||r.mids.contains(&"COP_PRESENT")||target.contains(suffix){return true;}
 // The existing progressive look-ahead can replace the final a/e by I+yor.
 // Allow all four vowels: no context-dependent decision is made here.
 if r.output.contains(&"VERB")&&suffix.ends_with(['a','e']){
  let mut base=suffix.to_owned();base.pop();
  for vowel in ['ı','i','u','ü']{if target.contains(&format!("{base}{vowel}yor")){return true;}}
 }
 false
}
#[cfg(any(suffix_plan,test))] #[path="suffix_plan.rs"] mod plan;
#[cfg(suffix_plan_oracle)] thread_local! {static ORACLE:Cell<[u64;2]>=const{Cell::new([0;2])};}
pub fn plan_info()->[usize;7] {
 #[cfg(suffix_plan)] {plan::info()}
 #[cfg(not(suffix_plan))] {[0,0,ROWS.len(),0,0,0,0]}
}
#[cfg(suffix_plan_oracle)] pub fn oracle_info()->[u64;2]{ORACLE.with(Cell::get)}
#[cfg(suffix_plan_oracle)] pub fn check_text(raw:&str)->usize{
 let target=crate::unicode::lower(raw).replace('’',"'").replace('\'',"");
 mask(&target).len()
}
pub(crate) fn mask(target:&str)->Vec<bool>{
 #[cfg(suffix_plan)] {
  let result=plan::mask(target);
  #[cfg(suffix_plan_oracle)] {
   let expected:Vec<bool>=ROWS.iter().map(|r|possible(r,target)).collect();
   assert_eq!(result,expected,"suffix mask differs for {target:?}");
   ORACLE.with(|c|{let a=c.get();c.set([a[0]+1,a[1]+ROWS.len() as u64]);});
  }
  result
 }
 #[cfg(not(suffix_plan))] {ROWS.iter().map(|r|possible(r,target)).collect()}
}

#[cfg(test)]mod tests{
 use super::*;use crate::{surface,lexicon::Lexeme};use std::path::Path;
 #[test]fn every_prefix_acceptance_survives(){
  let cfg=surface::Config::open(&Path::new("V:/TurkTokenizer/Deneyler/P81-20260916/data/surface")).unwrap();
  let mut checked=0u64;let mut accepted=0u64;
  for root in ["ev","kitap","git","ye","de","a","e","gel","gör","çağ","İ","ß","𐐀"]{
   for pos in ["VERB","NOUN"]{
    let e=Lexeme{id:"synthetic".into(),lemma:root.into(),stem:root.into(),pos:pos.into(),pronunciation:root.into(),secondary:String::new(),line:0,attrs:vec!["Voicing".into()]};
    for has_ids in [false,true]{
     let node=surface::Node{surface:root.into(),pos:pos.into(),phase:"V".into(),has_ids,mids:vec![]};
     for row in ROWS{
      let sr=row.surface_row();let full=format!("{root}{}",row.suffix());
      let mut targets=vec![full.clone(),format!("{full}lar"),root.into(),"yiyor".into(),"alakasız".into()];
      if full.ends_with(['a','e']){let mut stem=full.clone();stem.pop();for v in ['ı','i','u','ü']{targets.push(format!("{stem}{v}yordu"));}}
      for mid in row.mids{for target in &targets{
       let pass=surface::prefix(&cfg,&node,&e,&sr,mid,&full,target).unwrap();checked+=1;
       if pass{accepted+=1;assert!(possible(row,target),"row={} mid={} root={} target={}",row.id,mid,root,target);}
      }}
     }
    }
   }
  }
  eprintln!("PREFIX_IMPLICATION checked={checked} accepted={accepted}");assert!(checked>100000);
 }
 #[test]fn frozen_mid_error_shapes(){
  for (rid,row) in ROWS.iter().enumerate(){
   if !crate::rule_data::by_class(row.class).contains(&rid){continue;}
   for mid in row.mids{
   if mid.starts_with("POSS_")||mid.starts_with("AGR_"){assert_eq!(mid.split('_').count(),3,"{mid}");}
   if mid.starts_with("VOICE_"){assert!(["VOICE_CAUS","VOICE_PASS","VOICE_RECIP","VOICE_REFL"].contains(mid),"{mid}");}
  }}
 }
}

#[cfg(test)]mod plan_tests {
 use super::*;
 #[test]fn all_rows_unicode_and_constructed_targets(){
  let mut targets=std::collections::BTreeSet::new();
  for s in ["","ev","evlerimizden","GELİYOR","İIıi","I\u{307}","e\u{301}","a\0yor","🙂","𐐀","Ankara’da","ev''de","ß","é","ıyori yoruy orüyor","TAM_IMP"] {targets.insert(s.to_owned());}
  for row in ROWS {
   let s=row.suffix();targets.insert(s.to_owned());targets.insert(format!("x{s}y"));targets.insert(format!("ev{s}{s}"));
   if s.ends_with(['a','e']) {let mut base=s.to_owned();base.pop();for v in ['ı','i','u','ü']{targets.insert(format!("{base}{v}yor"));targets.insert(format!("x{base}{v}yordu"));}}
  }
  let alphabet=['a','e','ı','i','u','ü','y','o','r','İ','I','\0','\u{301}','𐐀','🙂','’','\''];
  let mut rng=1162026u64;
  for n in 0..4096{let mut text=String::new();for _ in 0..n%37{rng=rng.wrapping_mul(6364136223846793005).wrapping_add(1);text.push(alphabet[(rng>>32)as usize%alphabet.len()]);}targets.insert(text);}
  let mut comparisons=0usize;
  for raw in &targets {
   let normalized=crate::unicode::lower(raw).replace('’',"'").replace('\'',"");
   for t in [raw.as_str(),normalized.as_str()] {
    let expected:Vec<bool>=ROWS.iter().map(|r|possible(r,t)).collect();
    assert_eq!(plan::mask(t),expected,"target={t:?}");comparisons+=ROWS.len();
   }
  }
  eprintln!("PLAN_EQ targets={} row_comparisons={} info={:?}",targets.len(),comparisons,plan::info());
 }
 #[test]fn flags_remain_part_of_predicate_identity(){
  // Synthetic Row pairs exercise equal suffix text with different semantic flags.
  for suffix in ["a","e","la","le","x"] {
   for flag in ["","TAM_IMP","COP_PRESENT"] {
    let unconditional=!flag.is_empty();
    let make=|verb|Row{id:"test",surface:Some(suffix),class:"x",mids:match flag{"TAM_IMP"=>&["TAM_IMP"],"COP_PRESENT"=>&["COP_PRESENT"],_=>&[]},input:&[],output:if verb{&["VERB"]}else{&[]},pattern:None,enabled:false,kind:"",policy:"",family:"",license:"",roots:&[],handler:"",left:&[],right:&[],licensed:false};
    let noun=make(false);let verb=make(true);
    for empty_surface in [None,Some("")] {
     let mut row=make(false);row.surface=empty_surface;
     for t in ["","arbitrary","\0"]{assert_eq!(plan::mask_rows(std::slice::from_ref(&row),t),vec![possible(&row,t)]);assert!(possible(&row,t));}
    }
    for target in ["","qqq","ıyor","iyor","uyor","üyor","lıyor","liyor","luyor","lüyor","x","ax","la","le"] {
     let pair=[make(false),make(true)];
     assert_eq!(plan::mask_rows(&pair,target),pair.iter().map(|r|possible(r,target)).collect::<Vec<_>>());
    }
    assert_eq!(possible(&noun,"qqq"),unconditional);
    assert_eq!(possible(&verb,"qqq"),unconditional);
    if suffix.ends_with(['a','e']) && !unconditional {
     let mut stem=suffix.to_owned();stem.pop();let target=format!("{stem}ıyor");
     assert!(!possible(&noun,&target));assert!(possible(&verb,&target));
    }
   }
  }
 }
}
