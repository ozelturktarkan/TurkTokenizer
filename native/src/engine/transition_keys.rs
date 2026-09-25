//! Static field names only; no change to feature values or first-match semantics.
use std::borrow::Cow;
use crate::rule_values::{Ctx,Val};
#[cfg(any(transition_keys_audit,transition_keys_oracle))]
thread_local!{static COUNTS:std::cell::Cell<[u64;7]>=const{std::cell::Cell::new([0;7])};}
#[inline]fn add(i:usize,n:u64){
 #[cfg(any(transition_keys_audit,transition_keys_oracle))]COUNTS.with(|c|{let mut x=c.get();x[i]+=n;c.set(x)});
 #[cfg(not(any(transition_keys_audit,transition_keys_oracle)))]let _=(i,n);
}
pub fn counts()->[u64;7]{
 #[cfg(any(transition_keys_audit,transition_keys_oracle))]{COUNTS.with(|c|c.get())}
 #[cfg(not(any(transition_keys_audit,transition_keys_oracle)))]{[0;7]}
}
pub fn reset(){#[cfg(any(transition_keys_audit,transition_keys_oracle))]COUNTS.with(|c|c.set([0;7]));}
#[inline]
pub fn put(c:&mut Ctx,k:&'static str,v:Val){
 #[cfg(transition_keys_oracle)]let expected={let mut x=c.clone();crate::rule_values::put(&mut x,k,v.clone());x};
 add(0,1);
 if let Some((_,old))=c.iter_mut().find(|(key,_)|key.as_ref()==k){*old=v;add(2,1);}
 else{c.push((Cow::Borrowed(k),v));add(1,1);add(6,k.len()as u64);}
 #[cfg(transition_keys_oracle)]{assert_eq!(*c,expected,"P119 first-match/value/order");add(5,1);}
}
#[inline]
pub fn fields(pairs:&[(&'static str,&str)])->Ctx{
 let result:Ctx=pairs.iter().map(|(k,v)|(Cow::Borrowed(*k),Val::s(v))).collect();
 add(3,1);add(4,pairs.len()as u64);add(6,pairs.iter().map(|(k,_)|k.len()as u64).sum());
 #[cfg(transition_keys_oracle)]{
  let expected:Ctx=pairs.iter().map(|(k,v)|(k.to_string().into(),Val::s(v))).collect();
  assert_eq!(result,expected,"P119 initializer order/duplicates");add(5,1);
 }
 result
}
#[cfg(test)]mod tests{
 use super::*;use crate::rule_values::{ctx_write,get};
 use std::{collections::hash_map::DefaultHasher,hash::{Hash,Hasher}};
 fn encoded(c:&Ctx)->Vec<u8>{let mut b=Vec::new();ctx_write(c,&mut b).unwrap();b}
 fn hash(c:&Ctx)->u64{let mut h=DefaultHasher::new();c.hash(&mut h);h.finish()}
 #[test]fn first_match_types_unicode_order_hash_and_wire(){
  let keys=["Number","Person","Mood","Person[psor]","Number[psor]","Case","Voice","Polarity","VerbForm","Tense","Evident","Aspect","VoiceChain","","İ🙂"];
  let vals=[Val::Null,Val::Bool(false),Val::Bool(true),Val::Int(-7),Val::s(""),Val::s("ıİâ🙂"),Val::Set(vec!["a".into(),"b".into()]),Val::List(vec![Val::Int(1),Val::s("ö")])];
  for key in keys{for value in &vals{for c in [
   vec![],vec![(Cow::Owned(key.to_owned()),Val::s("first"))],
   vec![(Cow::Borrowed("other"),Val::Null),(Cow::Borrowed(key),Val::s("first")),(Cow::Owned(key.to_owned()),Val::s("second"))]
  ]{
   let mut got=c.clone();let mut expected=c.clone();put(&mut got,key,value.clone());crate::rule_values::put(&mut expected,key,value.clone());
   assert_eq!(got,expected);assert_eq!(encoded(&got),encoded(&expected));assert_eq!(hash(&got),hash(&expected));
   assert_eq!(get(&got,key),Some(value));
   if c.is_empty(){assert!(matches!(got[0].0,Cow::Borrowed(_)));}
   if c.len()==1{assert!(matches!(got[0].0,Cow::Owned(_)));}
   if c.len()==3{assert_eq!(got[2],c[2]);}
  }}}
 }
 #[test]fn initialization_preserves_duplicates_and_clone_independence(){
  for pairs in [vec![],vec![("Mood","Ind")],vec![("Number","Sing"),("Number","Plur"),("İ🙂","ö")]]{
   let got=fields(&pairs);let expected:Ctx=pairs.iter().map(|(k,v)|(k.to_string().into(),Val::s(v))).collect();
   assert_eq!(got,expected);assert_eq!(encoded(&got),encoded(&expected));assert_eq!(hash(&got),hash(&expected));
   assert!(got.iter().all(|(k,_)|matches!(k,Cow::Borrowed(_))));
   let mut assigned=vec![(Cow::Owned("old".into()),Val::Null)];assigned.clone_from(&got);assert_eq!(assigned,expected);assert_eq!(encoded(&assigned),encoded(&expected));assert_eq!(hash(&assigned),hash(&expected));
   let mut reverse=got.clone();reverse.clone_from(&expected);assert_eq!(encoded(&reverse),encoded(&expected));assert_eq!(hash(&reverse),hash(&expected));
   let mut clone=got.clone();put(&mut clone,"Number",Val::s("changed"));assert_eq!(got,expected);
  }
 }
 #[test]fn audit_counts_insertion_replacement_and_initialization(){
  reset();let mut c=fields(&[("A","a"),("B","b")]);put(&mut c,"A",Val::Null);put(&mut c,"New",Val::Bool(true));
  let x=counts();assert_eq!(&x[..5],&[2,1,1,1,2]);assert_eq!(x[6],5);
  #[cfg(transition_keys_oracle)]assert_eq!(x[5],3);
 }
}
