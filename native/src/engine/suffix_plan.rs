//! Immutable rule predicates; no target strings or answers survive a call.
use std::sync::OnceLock;
use crate::rule_data::{Row,ROWS};
struct Predicate { suffix:&'static str, progressive:bool, variants:Vec<String> }
struct Plan { predicates:Vec<Predicate>, rows:Vec<usize> }
const ALWAYS:usize=usize::MAX;
static PLAN:OnceLock<Plan>=OnceLock::new();
fn always(r:&Row)->bool {r.suffix().is_empty()||r.mids.contains(&"TAM_IMP")||r.mids.contains(&"COP_PRESENT")}
fn build()->Plan {build_rows(ROWS)}
fn build_rows(source:&[Row])->Plan {
 let mut predicates:Vec<Predicate>=Vec::new();let mut rows=Vec::with_capacity(source.len());
 for r in source {
  if always(r){rows.push(ALWAYS);continue;}
  let suffix=r.surface.unwrap_or("");
  let progressive=r.output.contains(&"VERB")&&suffix.ends_with(['a','e']);
  let index=match predicates.iter().position(|p|p.suffix==suffix&&p.progressive==progressive) {
   Some(i)=>i,
   None=>{
    let variants=if progressive {
     let mut base=suffix.to_owned();base.pop();
     ['ı','i','u','ü'].into_iter().map(|v|format!("{base}{v}yor")).collect()
    }else{Vec::new()};
    let i=predicates.len();predicates.push(Predicate{suffix,progressive,variants});i
   }
  };
  rows.push(index);
 }
 Plan{predicates,rows}
}
pub(super) fn mask(target:&str)->Vec<bool> {
 evaluate(PLAN.get_or_init(build),target)
}
#[cfg(test)] pub(super) fn mask_rows(rows:&[Row],target:&str)->Vec<bool>{evaluate(&build_rows(rows),target)}
fn evaluate(p:&Plan,target:&str)->Vec<bool>{
 let values:Vec<bool>=p.predicates.iter().map(|g|target.contains(g.suffix)||g.variants.iter().any(|v|target.contains(v.as_str()))).collect();
 p.rows.iter().map(|&i|i==ALWAYS||values[i]).collect()
}
// Reading this diagnostic never initializes the plan; allocator bookkeeping is excluded.
pub(super) fn info()->[usize;7] {
 let static_bytes=std::mem::size_of::<OnceLock<Plan>>();
 let Some(p)=PLAN.get()else{return [1,0,ROWS.len(),0,0,static_bytes,0]};
 let variants=p.predicates.iter().map(|g|g.variants.iter().map(|s|s.capacity()).sum::<usize>()).sum::<usize>();
 let heap=p.rows.capacity()*std::mem::size_of::<usize>()+p.predicates.capacity()*std::mem::size_of::<Predicate>()
  +p.predicates.iter().map(|g|g.variants.capacity()*std::mem::size_of::<String>()).sum::<usize>()+variants;
 [1,1,p.rows.len(),p.predicates.len(),heap,static_bytes,variants]
}
