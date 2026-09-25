// Modified for public 0.1.0rc1: local module path and decode protocol; frozen engine unchanged.
#![windows_subsystem = "windows"]
extern crate turktokenizer_p82 as p82;
mod binding;
mod bpe;
use std::{collections::BTreeSet,io::{self,BufRead,Write},path::Path,time::Instant};
use p82::{json::{self,V,s,f},obj,Tokenizer};
fn arr(v:&V)->io::Result<&[V]>{if let V::Array(xs)=v{Ok(xs)}else{Err(json::err("array"))}}
fn run(v:&V,rt:&mut Option<Tokenizer>,data:&Path,frames:&BTreeSet<String>,bpe:&bpe::Bpe)->io::Result<V>{
    match v.get("op").string()? {
        "decode"=>{
            if rt.is_none(){*rt=Some(Tokenizer::open(data,4194304)?);}
            let ids=arr(v.get("ids"))?.iter().map(|x|u32::try_from(x.usize()?).map_err(|_|json::err("ID exceeds u32"))).collect::<io::Result<Vec<u32>>>()?;
            Ok(obj!("text":s(rt.as_mut().unwrap().decode(&ids)?)))
        },
        "solve"=>binding::solve(v.get("input"),frames),
        "bpe"=>{let t=Instant::now();let ids=bpe.encode(v.get("text").string()?);let elapsed=t.elapsed().as_secs_f64();
            let decoded=String::from_utf8(bpe.decode(&ids)?).map_err(|_|json::err("BPE UTF8"))?;
            Ok(obj!("ids":V::Array(ids.iter().map(|&i|json::n(i as usize)).collect()),"decoded":s(decoded),"encode_seconds":f(elapsed)))},
        "baseline"|"analyze"=>{
            if rt.is_none(){*rt=Some(Tokenizer::open(data,4194304)?);}
            let timer=Instant::now();
            let baseline_only=v.get("op").text()=="baseline";
            let(a,t)=rt.as_mut().unwrap().analyze(v.get("text").string()?,!baseline_only)?;
            let native_seconds=timer.elapsed().as_secs_f64();
            if baseline_only{return Ok(a);}
            let timer=Instant::now();
            let budget=if v.has("node_budget"){v.get("node_budget").usize()?}else{200000};
            let sidecar=binding::from_audit(&a,&t,budget).and_then(|input|binding::solve(&input,frames));
            let graph=match sidecar{Ok(x)=>x,Err(e)=>obj!("status":s("SIDECAR_ERROR"),"error":s(e.to_string()),"baseline_override_allowed":V::Bool(false))};
            Ok(obj!("baseline":a,"baseline_trace":t,"binding":graph,"native_seconds":f(native_seconds),"binding_seconds":f(timer.elapsed().as_secs_f64()),
                "runtime_python_required":V::Bool(false)))
        },
        _=>Err(json::err("unknown operation"))
    }
}
fn main()->io::Result<()>{
    let args:Vec<String>=std::env::args().collect();if args.len()!=4{return Err(json::err("usage: binding.exe P81_DATA FRAMES_JSON BPE_BIN"));}
    let cfg=json::parse(&std::fs::read_to_string(&args[2])?)?;
    let mut frames=BTreeSet::new();for f in arr(cfg.get("frames"))?{frames.insert(f.get("lemma").string()?.to_owned());}
    let bpe=bpe::Bpe::open(Path::new(&args[3]))?;
    let mut rt=None;let input=io::stdin();let mut output=io::BufWriter::new(io::stdout().lock());
    for line in input.lock().lines(){
        let result=json::parse(&line?).and_then(|v|run(&v,&mut rt,Path::new(&args[1]),&frames,&bpe));
        let out=match result{Ok(v)=>obj!("ok":V::Bool(true),"result":v),Err(e)=>obj!("ok":V::Bool(false),"error":s(e.to_string()))};
        writeln!(output,"{}",out.dump())?;output.flush()?;
    }
    Ok(())
}
