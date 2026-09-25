use std::sync::atomic::{AtomicU64,Ordering};
use crate::json::{V,n,f};
static CALLS:[AtomicU64;4]=[const{AtomicU64::new(0)};4];
static NS:[AtomicU64;4]=[const{AtomicU64::new(0)};4];
pub fn record(index:usize,ns:u128){CALLS[index].fetch_add(1,Ordering::Relaxed);NS[index].fetch_add(ns as u64,Ordering::Relaxed);}
pub fn snapshot()->V { V::Object(["table_get","lexeme_at","lexeme_seeds","replay_entry"].iter().enumerate().map(|(i,k)|(k.to_string(),crate::obj!("calls":n(CALLS[i].load(Ordering::Relaxed) as usize),"seconds":f(NS[i].load(Ordering::Relaxed) as f64/1e9)))).collect()) }
