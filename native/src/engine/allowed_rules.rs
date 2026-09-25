//! Lists live for one search only; dynamic class/PROPN decisions remain in search.
use crate::rule_data::{ROWS,by_class};
pub(crate) struct ClassPlan {pub pairs:Vec<(usize,&'static str)>,pub skipped:u64}
pub(crate) struct AllowedRules<'a> {
 mask:&'a[bool],
 slots:[Option<ClassPlan>;CLASS_COUNT+1],
 #[cfg(allowed_rules_audit)] heap:usize,
}
const CLASS_COUNT:usize=26;
const CLASSES:[&str;CLASS_COUNT]=["atE","bfE","bvE","clE","ctE","ffE","fiE","flE","fsE","hlE","ifE","iiE","isE","kcE","ksE","olE","sdE","sfE","siE","syE","vtE","ybE","ylE","ypE","zmE","zyE"];
fn index(class:&str)->usize {match class {"atE"=>0,"bfE"=>1,"bvE"=>2,"clE"=>3,"ctE"=>4,"ffE"=>5,"fiE"=>6,"flE"=>7,"fsE"=>8,"hlE"=>9,"ifE"=>10,"iiE"=>11,"isE"=>12,"kcE"=>13,"ksE"=>14,"olE"=>15,"sdE"=>16,"sfE"=>17,"siE"=>18,"syE"=>19,"vtE"=>20,"ybE"=>21,"ylE"=>22,"ypE"=>23,"zmE"=>24,"zyE"=>25, _=>CLASS_COUNT}}
fn build(rids:&[usize],mask:&[bool])->ClassPlan{
 let mut pairs=Vec::new();let mut skipped=0;
 for &rid in rids {
  append_row(&mut pairs,&mut skipped,rid,ROWS[rid].mids,mask[rid]);
 }
 ClassPlan{pairs,skipped}
}
fn append_row(pairs:&mut Vec<(usize,&'static str)>,skipped:&mut u64,rid:usize,mids:&[&'static str],allowed:bool){
 if allowed{for &mid in mids{pairs.push((rid,mid));}}else{*skipped+=mids.len() as u64;}
}
#[cfg(any(test,allowed_rules_oracle))]
fn original(rids:&[usize],mask:&[bool])->ClassPlan{
 let mut pairs=Vec::new();let mut skipped=0;
 for rid in rids{for mid in ROWS[*rid].mids{
  if !mask[*rid]{skipped+=1;continue;}
  pairs.push((*rid,*mid));
 }}
 ClassPlan{pairs,skipped}
}
impl<'a> AllowedRules<'a> {
 pub fn new(mask:&'a[bool])->Self{
  assert_eq!(mask.len(),ROWS.len());
  #[cfg(allowed_rules_audit)] add(0,1);
  Self{mask,slots:std::array::from_fn(|_|None),#[cfg(allowed_rules_audit)] heap:0}
 }
 pub fn class(&mut self,class:&str)->&ClassPlan{
  let i=index(class);
  if self.slots[i].is_none(){
   #[cfg(allowed_rules_audit)] let start=std::time::Instant::now();
   let rids=by_class(class);let plan=build(rids,self.mask);
   #[cfg(allowed_rules_audit)] {
    add(1,1);add(3,rids.len() as u64);add(4,plan.pairs.len() as u64);
    self.heap+=plan.pairs.capacity()*std::mem::size_of::<(usize,&'static str)>();
    maximum(6,self.heap as u64);add(7,start.elapsed().as_nanos() as u64);
   }
   #[cfg(allowed_rules_oracle)] {
    let expected=original(rids,self.mask);
    assert_eq!(plan.pairs,expected.pairs,"allowed pairs order/multiplicity for {class}");
    assert_eq!(plan.skipped,expected.skipped,"skipped mids for {class}");
    #[cfg(allowed_rules_audit)] add(8,1);
   }
   self.slots[i]=Some(plan);
  }
  let plan=self.slots[i].as_ref().unwrap();
  #[cfg(allowed_rules_audit)] {add(2,1);add(5,plan.skipped);add(9,plan.pairs.len() as u64);}
  plan
 }
}
#[cfg(allowed_rules_audit)]
thread_local!{static COUNTS:std::cell::Cell<[u64;10]>=const{std::cell::Cell::new([0;10])};}
#[cfg(allowed_rules_audit)] fn add(i:usize,v:u64){COUNTS.with(|c|{let mut a=c.get();a[i]+=v;c.set(a);});}
#[cfg(allowed_rules_audit)] fn maximum(i:usize,v:u64){COUNTS.with(|c|{let mut a=c.get();a[i]=a[i].max(v);c.set(a);});}
#[cfg(allowed_rules_audit)] pub fn reset(){COUNTS.with(|c|c.set([0;10]));}
#[cfg(allowed_rules_audit)] pub fn info()->Vec<u64>{
 let mut v=COUNTS.with(|c|c.get().to_vec());
 // Primary AllowedRules has only mask and slots; audit-only heap field excluded.
 v.push((std::mem::size_of::<&[bool]>()+std::mem::size_of::<[Option<ClassPlan>;CLASS_COUNT+1]>())as u64);
 v.push(std::mem::size_of::<(usize,&'static str)>()as u64);v
}
#[cfg(test)]mod tests{
 use super::*;
 fn compare(plan:&ClassPlan,rids:&[usize],mask:&[bool]){
  let expected=original(rids,mask);assert_eq!(plan.pairs,expected.pairs);assert_eq!(plan.skipped,expected.skipped);
 }
 #[test]fn all_masks_classes_order_and_reuse(){
  let mut rng=1172026u64;let mut masks=vec![vec![false;ROWS.len()],vec![true;ROWS.len()]];
  for _ in 0..256 {masks.push((0..ROWS.len()).map(|_|{rng=rng.wrapping_mul(6364136223846793005).wrapping_add(1);rng>>63!=0}).collect());}
  for mask in &masks {
   let mut plan=AllowedRules::new(mask);assert!(plan.slots.iter().all(Option::is_none));
   for (i,class) in CLASSES.iter().enumerate(){
    assert_eq!(index(class),i);let a=plan.class(class);compare(a,by_class(class),mask);let ptr=a.pairs.as_ptr();let cap=a.pairs.capacity();
    let b=plan.class(class);assert_eq!(b.pairs.as_ptr(),ptr);assert_eq!(b.pairs.capacity(),cap);
   }
   for class in ["","missing","İ","🙂"] {let a=plan.class(class);compare(a,by_class(class),mask);assert!(a.pairs.is_empty());assert_eq!(a.skipped,0);}
  }
  // A new search must not inherit any populated slot or former target's mask.
  let a=vec![false;ROWS.len()];let b=vec![true;ROWS.len()];
  let mut first=AllowedRules::new(&a);let mut second=AllowedRules::new(&b);
  first.class(CLASSES[0]);assert!(second.slots.iter().all(Option::is_none));compare(second.class(CLASSES[0]),by_class(CLASSES[0]),&b);
  eprintln!("ALLOWED_MASKS masks={} classes={}",masks.len(),CLASSES.len());
 }
 #[test]fn duplicate_rids_and_empty_multiple_mids(){
  let mut rids:Vec<usize>=(0..ROWS.len()).rev().collect();rids.extend(0..ROWS.len());rids.extend([0,0,1,1]);
  for mask in [vec![false;ROWS.len()],vec![true;ROWS.len()],(0..ROWS.len()).map(|i|i%2==0).collect()]{
   compare(&build(&rids,&mask),&rids,&mask);compare(&build(&[],&mask),&[],&mask);
  }
  assert!(ROWS.iter().any(|r|r.mids.len()>1));
 }
 #[test]fn class_index_covers_frozen_lookup(){
  let source=include_str!("rule_data.rs");let lookup=source.split("pub fn by_class").nth(1).unwrap().split("_=>&[]}}").next().unwrap();
  let names:Vec<_>=lookup.lines().filter_map(|l|l.strip_prefix('"').map(|s|s.split('"').next().unwrap())).collect();
  assert_eq!(names,CLASSES);
  for r in ROWS{if !by_class(r.class).is_empty(){assert!(index(r.class)<CLASS_COUNT);}}
 }
 #[test]fn synthetic_empty_and_duplicate_mids(){
  for allowed in [false,true]{
   let mut pairs=Vec::new();let mut skipped=0;
   append_row(&mut pairs,&mut skipped,7,&[],allowed);
   append_row(&mut pairs,&mut skipped,9,&["x","x","y"],allowed);
   append_row(&mut pairs,&mut skipped,9,&["x"],allowed);
   if allowed{assert_eq!(pairs,vec![(9,"x"),(9,"x"),(9,"y"),(9,"x")]);assert_eq!(skipped,0);}
   else{assert!(pairs.is_empty());assert_eq!(skipped,4);}
  }
 }
 #[cfg(allowed_rules_audit)] #[test]fn audit_confirms_lazy_build_once_and_new_search(){
  reset();let mask=vec![true;ROWS.len()];
  {let mut p=AllowedRules::new(&mask);assert_eq!(info()[1],0);p.class(CLASSES[0]);p.class(CLASSES[0]);assert_eq!(info()[1],1);}
  {let mut p=AllowedRules::new(&mask);p.class(CLASSES[0]);}
  let a=info();assert_eq!(&a[..3],&[2,2,3]);assert_eq!(a[5],0);
 }

}
