//! Python-free inference with the frozen P21 behavior contract.
mod search;mod search_state;mod search_json;mod search_metadata;
mod rule_values;mod rule_data;mod rule_transition;mod rule_context;mod rules;
mod surface;mod lexicon;mod raw;mod raw_props;mod codec;mod boundary;mod text_props;
mod wire;mod math;mod tables;mod ranking;mod gate;mod unicode;mod features;mod numeric;
pub mod json;mod projection;pub mod runtime;mod integrity;

pub use runtime::Runtime as Tokenizer;

/// Diagnostic-only explicit root for active early-exit/limit tests; never used by encode.
#[cfg(candidate_profile)]
pub fn diagnostic_search_profiled(rt:&mut Tokenizer,raw:&str,limits:[u32;3])->std::io::Result<(json::V,json::V)>{
 let _root=candidate_profile::Span::enter(candidate_profile::ROOT);
 diagnostic_search(rt,raw,limits)
}



pub mod paged_file;

pub mod suffix_filter;
pub mod transition_keys;
#[macro_export]macro_rules! p119_ps{($c:expr,$k:expr,$v:expr)=>{
 {#[cfg(transition_keys)]{$crate::transition_keys::put($c,$k,$crate::rule_values::Val::s($v))}
 #[cfg(not(transition_keys))]{$crate::rule_transition::ps($c,$k,$v)}}
};}
#[macro_export]macro_rules! p119_put{($c:expr,$k:expr,$v:expr)=>{
 {#[cfg(transition_keys)]{$crate::transition_keys::put($c,$k,$v)}
 #[cfg(not(transition_keys))]{$crate::rule_values::put($c,$k,$v)}}
};}


#[cfg(rule_sample)] pub mod rule_sample;
#[macro_export]macro_rules! p118_expr{($label:ident,$value:expr)=>{
 {#[cfg(rule_sample)]{let _stage=$crate::rule_sample::Stage::enter($crate::rule_sample::$label);$value}
 #[cfg(not(rule_sample))]{$value}}
};}
#[macro_export]macro_rules! p118_end{($label:ident)=>{
 #[cfg(rule_sample)]{$crate::rule_sample::terminal($crate::rule_sample::$label);}
};}
#[macro_export]macro_rules! p118_search_apply{($value:expr)=>{
 {#[cfg(rule_sample)]{let call=$crate::rule_sample::Call::search();let result=$value;call.finish(&result);result}
 #[cfg(not(rule_sample))]{$value}}
};}
#[macro_export]macro_rules! p118_license{($value:expr)=>{
 {#[cfg(rule_sample)]{$crate::rule_sample::licensed();}$value}
};}

#[cfg(any(allowed_rules,test))] pub mod allowed_rules;

/// Research-only raw-search inspection, with the original frozen limit bounds.
pub fn diagnostic_search(rt:&mut Tokenizer,raw:&str,limits:[u32;3])->std::io::Result<(json::V,json::V)>{
 if limits[0]>20000||limits[1]>256||limits[2]>20{return Err(json::err("frozen search limit range"));}
 let(a,b)=search::search(raw,limits,&mut rt.provider.lex,&mut rt.provider.config)?;
 Ok((json::parse(&a)?,json::parse(&b)?))
}

#[cfg(node_oracle)]
pub fn diagnostic_node_reuse_checks()->[u64;4]{search_state::node_checks()}

#[cfg(context_oracle)]
#[path="../oracle_context.rs"] mod oracle_context;
#[cfg(context_oracle)]
#[path="../context_audit.rs"] mod context_audit;
#[cfg(context_oracle)]
pub fn diagnostic_context_counts()->[u64;9]{context_audit::counts()}
#[cfg(context_oracle)]
pub fn diagnostic_context_self_check()->[u64;5]{context_audit::self_check()}

#[cfg(phonetic_oracle)]
#[path="../phonetic_audit.rs"] mod phonetic_audit;
#[cfg(phonetic_oracle)]
pub fn diagnostic_phonetic_counts()->[u64;4]{phonetic_audit::counts()}
#[cfg(phonetic_oracle)]
pub fn diagnostic_phonetic_self_check()->[u64;5]{phonetic_audit::self_check()}

#[cfg(lookup_index)] pub mod lookup_index;
#[cfg(candidate_profile)] pub mod candidate_profile;
#[macro_export] macro_rules! p112_expr{($label:ident,$value:expr)=>{{
 #[cfg(candidate_profile)]{let _p112_scope=$crate::candidate_profile::Span::enter($crate::candidate_profile::$label);$value}
 #[cfg(not(candidate_profile))]{$value}
}};}
#[macro_export] macro_rules! p112_event{($id:ident,$value:expr)=>{
 #[cfg(candidate_profile)]{$crate::candidate_profile::event($crate::candidate_profile::$id,$value as u64);}
};}

