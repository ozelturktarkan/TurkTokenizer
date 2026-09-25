#![cfg_attr(windows, windows_subsystem = "windows")]
mod search;mod search_state;mod search_json;mod search_metadata;
mod rule_values;mod rule_data;mod rule_transition;mod rule_context;mod rules;
mod surface;mod lexicon;mod raw;mod raw_props;mod codec;mod boundary;mod text_props;
mod wire;mod math;mod tables;mod ranking;mod gate;mod unicode;mod features;mod numeric;
mod json;mod projection;mod runtime;mod integrity;
use std::{io::{self,BufRead,Write},path::PathBuf};
use json::{V,s,n,f};
#[repr(C)]
#[derive(Default)]
struct Memory {cb:u32,faults:u32,peak:usize,working:usize,peak_paged:usize,paged:usize,peak_nonpaged:usize,nonpaged:usize,commit:usize,peak_commit:usize}
#[link(name="kernel32")]
extern "system" {fn GetCurrentProcess()->*mut std::ffi::c_void;fn K32GetProcessMemoryInfo(handle:*mut std::ffi::c_void,data:*mut Memory,bytes:u32)->i32;}
fn memory()->io::Result<V>{
    let mut m=Memory::default();m.cb=std::mem::size_of::<Memory>() as u32;let size=m.cb;
    if unsafe{K32GetProcessMemoryInfo(GetCurrentProcess(),&mut m,size)}==0{return Err(io::Error::last_os_error());}
    Ok(obj!("pid":n(std::process::id() as usize),"working_set_bytes":n(m.working),"private_bytes":n(m.commit),"peak_working_set_bytes":n(m.peak)))
}
fn info(m:&runtime::Runtime)->io::Result<V>{Ok(obj!("implementation":s("P82-STANDALONE-RUST-v1"),"behavior_contract":s("S06E-P21-Stable-v1.0.0"),
    "python_required":V::Bool(false),"vocabulary_size":n(codec::COUNT as usize),"weight_bytes":n(4194304),"cache":m.cache_info(),"memory":memory()?,"load_seconds":f(m.load_seconds),
    "phase_seconds":V::Object(["plan","candidates","ranking","gate","assembly"].iter().zip(m.phase_ns).map(|(name,ns)|(name.to_string(),f(ns as f64/1e9))).collect()))) }
fn get_ids(v:&V)->io::Result<Vec<u32>>{
    let V::Array(xs)=v else{return Err(json::err("ids must be an array"));};
    xs.iter().map(|v|u32::try_from(v.usize()?).map_err(|_|json::err("ID overflow"))).collect()
}
fn ids_json(ids:Vec<u32>)->V{V::Array(ids.into_iter().map(|id|n(id as usize)).collect())}
fn request(m:&mut runtime::Runtime,r:&V)->io::Result<V>{
    let op=r.get("op").string()?;
    match op {
        "info"=>Ok(obj!("ok":V::Bool(true),"result":info(m)?)),
        "clear_cache"=>{m.clear_cache();Ok(obj!("ok":V::Bool(true),"result":info(m)?))},
        "encode" if !r.get("audit").boolean()=>Ok(obj!("ok":V::Bool(true),"result":ids_json(m.encode(r.get("text").string()?)?))),
        "analyze"|"encode"=>{
            let (result,audit)=m.analyze(r.get("text").string()?,r.get("audit").boolean())?;
            let result=if op=="encode"{result.get("input_ids").clone()}else{result};
            let mut response=obj!("ok":V::Bool(true),"result":result);if r.get("audit").boolean(){response.set("audit",audit);}Ok(response)
        },
        "decode"=>Ok(obj!("ok":V::Bool(true),"result":s(m.decode(&get_ids(r.get("ids"))?)?))),
        "encode_bytes"=>{
            let h=r.get("hex").string()?;if h.len()%2!=0{return Err(json::err("hex byte length"));}
            let bytes:Vec<u8>=h.as_bytes().chunks(2).map(|b|std::str::from_utf8(b).ok().and_then(|s|u8::from_str_radix(s,16).ok()).ok_or_else(||json::err("hex bytes"))).collect::<io::Result<_>>()?;
            Ok(obj!("ok":V::Bool(true),"result":V::Array(codec::encode(&bytes).into_iter().map(|v|n(v as usize)).collect())))
        },
        "decode_bytes"=>Ok(obj!("ok":V::Bool(true),"result":s(m.decode_bytes(&get_ids(r.get("ids"))?)?.iter().map(|b|format!("{b:02x}")).collect::<String>()))),
        "candidates"=>Ok(obj!("ok":V::Bool(true),"result":m.candidates(r.get("text").string()?)?)),
        "raw_analysis"=>{
            let limits=if r.has("limits"){let xs=get_ids(r.get("limits"))?;if xs.len()!=3||xs[0]>20000||xs[1]>256||xs[2]>20{return Err(json::err("frozen search limit range"));}[xs[0],xs[1],xs[2]]}else{[20000,256,20]};
            let (result,stats)=search::search(r.get("text").string()?,limits,&mut m.provider.lex,&mut m.provider.config)?;
            Ok(obj!("ok":V::Bool(true),"result":json::parse(&result)?,"stats":json::parse(&stats)?))
        },
        _=>Err(json::err("unknown operation")),
    }
}
fn run()->io::Result<()>{
    let mut args=std::env::args().skip(1).collect::<Vec<_>>();
    let executable=std::env::current_exe()?;
    let directory=executable.parent().ok_or_else(||json::err("executable directory"))?;
    let mut data=directory.ancestors().take(3).map(|p|p.join("data")).find(|p|p.join("weights-f32.bin").is_file()).unwrap_or_else(||directory.join("data"));
    let mut cache_limit=4*1024*1024;
    while args.first().is_some_and(|s|s=="--data"||s=="--cache-bytes"){
        if args.len()<2{return Err(json::err("missing option value"));}
        if args[0]=="--data"{data=PathBuf::from(&args[1]);}else{cache_limit=args[1].parse().map_err(|_|json::err("cache size"))?;if cache_limit>256*1024*1024{return Err(json::err("cache size limit"));}}
        args.drain(..2);
    }
    if args.first().is_some_and(|s|s=="--help"){
        println!("TurkTokenizer P82: --jsonl | --text TEXT | --encode TEXT | --file UTF8_FILE | --decode JSON_IDS | --info\nOptional prefix: --data DIRECTORY --cache-bytes INTEGER\nInference is entirely Rust. Frozen P21 behavior; P78 reference. No Python runtime required.");return Ok(());
    }
    let mut model=runtime::Runtime::open(&data,cache_limit)?;
    let mode=args.first().map_or("--jsonl",String::as_str);
    if mode=="--jsonl"{
        let stdin=io::stdin();let mut input=stdin.lock();let stdout=io::stdout();let mut out=stdout.lock();let mut line=String::new();
        loop {line.clear();if input.read_line(&mut line)?==0{break;}
            let response=match json::parse(&line).and_then(|r|request(&mut model,&r)){Ok(v)=>v,Err(e)=>obj!("ok":V::Bool(false),"error":s(e.to_string()))};
            writeln!(out,"{}",response.dump())?;out.flush()?;
        }return Ok(());
    }
    let value=match mode {
        "--info"=>info(&model)?,
        "--text"|"--encode"|"--file"=>{
            let arg=args.get(1).ok_or_else(||json::err("missing input"))?;
            let text=if mode=="--file"{std::fs::read_to_string(arg)?}else{arg.clone()};if mode=="--encode"{ids_json(model.encode(&text)?)}else{model.analyze(&text,false)?.0}
        },
        "--decode"=>s(model.decode(&get_ids(&json::parse(args.get(1).ok_or_else(||json::err("missing IDs"))?)?)?)?),
        _=>return Err(json::err("unknown argument; use --help")),
    };
    println!("{}",value.dump());Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("P82: {e}");std::process::exit(2);}}


mod paged_file;
