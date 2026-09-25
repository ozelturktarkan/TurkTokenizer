use std::io;
use crate::{features,math,unicode};
use crate::tables::Frequencies;
use crate::ranking::FeatureMap;
mod model{include!("gate_model.rs");}
pub struct Decision {pub key:String,pub count:usize,pub margin:Option<f64>,pub probability:f64,pub flags:u32,pub safety:u32,pub evidence:Option<FeatureMap>}
pub struct Admission {pub accepted:bool,pub reason:&'static str,pub risk:Option<f64>,pub threshold:Option<f64>,pub logit:f64,pub baseline:FeatureMap,pub evidence:FeatureMap}
fn flag(b:bool)->f64{if b{1.0}else{0.0}}
fn get(fs:&FeatureMap,key:&str)->f64{fs.iter().find(|f|f.0==key).map_or(0.0,|f|f.1)}
fn update(fs:&mut FeatureMap,key:&str,value:f64){if let Some(row)=fs.iter_mut().find(|r|r.0==key){row.1=value;}else{fs.push((key.into(),value));}}
fn weighted(fs:&FeatureMap,parameters:&[(&str,u64,u64,u64)])->f64{
    let mut z=0.0;for &(key,w,mean,scale)in parameters{z+=f64::from_bits(w)*(get(fs,key)-f64::from_bits(mean))/f64::from_bits(scale);}z
}
fn no(reason:&'static str)->Admission{Admission{accepted:false,reason,risk:None,threshold:None,logit:0.0,baseline:Vec::new(),evidence:Vec::new()}}
pub fn decide(raw:&str,decision:Option<&Decision>,complete:bool,can_encode:bool,freq:&mut Frequencies)->io::Result<Admission>{
    let Some(d)=decision else{return Ok(no("NO_SUPPORTED_PATH"));};
    if !complete{return Ok(no("INCOMPLETE_SEARCH"));}
    if !can_encode{return Ok(no("MORPH_VOCAB_MISS"));}
    if d.safety==0{return Ok(no("P21_MISSING_NAME_CHECK"));}
    if d.safety==2{return Ok(no("P21_KNOWN_NAME_ROOT_AMBIGUITY"));}
    let Some(observed)=&d.evidence else{return Ok(no("P21_MISSING_CONTEXT_EVIDENCE"));};
    let (root,rp,events,fp)=features::path(&d.key)?;
    let wc=freq.word(raw)?;let mut total=0u64;let mut chosen_count=0;
    let mut roots:Vec<((String,String),u64)>=Vec::new();
    for(key,n)in &wc{
        total+=*n;if key==&d.key{chosen_count=*n;}
        let (r,p,_,_)=features::path(key)?;
        if let Some(row)=roots.iter_mut().find(|row|row.0.0==r && row.0.1==p){row.1+=*n;}else{roots.push(((r,p),*n));}
    }
    let selected=roots.iter().find(|row|row.0.0==root && row.0.1==rp).map_or(0,|r|r.1);
    let rival=roots.iter().filter(|row|row.0.0!=root||row.0.1!=rp).map(|r|r.1).max().unwrap_or(0);
    let global=freq.path(&d.key)?;
    let mut base:FeatureMap=vec![
        ("bias".into(),1.0),("log_candidates".into(),math::log1p(d.count as f64)),("unique_path".into(),flag(d.count==1)),
        ("probability".into(),d.probability),("logit".into(),math::log(d.probability.max(1e-6)/(1.0-d.probability).max(1e-6))),
        ("margin".into(),d.margin.map_or(0.0,|v|v.min(20.0))),("word_train_logcount".into(),math::log1p(total as f64)),
        ("path_train_logcount".into(),math::log1p(chosen_count as f64)),("word_prior_fraction".into(),if total>0{chosen_count as f64/total as f64}else{0.0}),
        ("global_path_logcount".into(),math::log1p(global as f64)),("root_surface_ratio".into(),root.chars().count()as f64/raw.chars().count().max(1)as f64),
        ("events".into(),events.len()as f64),("capitalized".into(),flag(unicode::first_upper(raw))),("allcaps".into(),flag(unicode::all_upper(raw))),
        ("apostrophe".into(),flag(raw.contains(['\'','’']))),("compound".into(),flag(d.flags&1!=0)),("name_reading".into(),flag(d.flags&2!=0)),("inflected_title".into(),flag(d.flags&4!=0)),
        (format!("RP={rp}"),1.0),(format!("FP={fp}"),1.0)
    ];
    for prefix in ["POSS_","CASE_","COP_","PART_","CONV_","VOICE_","TAM_"]{base.push((format!("HAS={prefix}"),flag(events.iter().any(|e|e.0.starts_with(prefix)))));}
    let mut ev=observed.clone();
    update(&mut ev,"ev_word_root_logcount",math::log1p(selected as f64));
    update(&mut ev,"ev_word_root_prior_fraction",if total>0{selected as f64/total as f64}else{0.0});
    update(&mut ev,"ev_other_root_word_prior_fraction",if total>0{rival as f64/total as f64}else{0.0});
    update(&mut ev,"ev_root_prior_conflict",flag(rival>selected));
    // Anchored model order is evidence sum first, then baseline sum.
    let z=weighted(&ev,model::EVIDENCE)+weighted(&base,model::ANCHOR);
    let risk=1.0/(1.0+math::exp(-z.clamp(-60.0,60.0)));
    let threshold=model::THRESHOLD.map(f64::from_bits);let accepted=threshold.is_some_and(|t|risk>=t);
    Ok(Admission{accepted,reason:if accepted{"P21_ESTIMATED_PATH_RISK"}else{"P21_LOW_PATH_CONFIDENCE"},risk:Some(risk),threshold,logit:z,baseline:base,evidence:ev})
}
