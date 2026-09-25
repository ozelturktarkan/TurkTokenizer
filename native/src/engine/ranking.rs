use std::io;
use crate::{features,math,numeric};
pub type Parsed=(String,String,Vec<(String,String)>,String);
pub type FeatureMap=Vec<(String,f64)>;
pub struct Candidate {pub key:String,pub preference:String,pub encodable:bool,pub flags:u32,pub first_surface:String,pub lexeme_id:String,pub forced:Option<[f64;3]>}
pub struct Ranked {pub ordered:Vec<(usize,[f64;3])>,pub selected:Option<usize>,pub margin:Option<f64>,pub probability:f64,pub evidence:FeatureMap,pub conflicts:Vec<usize>}
fn maximum(mut values:impl Iterator<Item=f64>)->f64{let mut best=values.next().unwrap();for v in values{if v>best{best=v;}}best}
fn flag(v:bool)->f64{if v{1.0}else{0.0}}
fn root_eq(a:&Parsed,b:&Parsed)->bool{a.0==b.0 && a.1==b.1}
fn frame_eq(a:&Parsed,b:&Parsed)->bool{
    root_eq(a,b) && a.3==b.3 && a.2.iter().filter(|e|!e.0.starts_with("CASE_")&&!e.0.starts_with("POSS_")).eq(b.2.iter().filter(|e|!e.0.starts_with("CASE_")&&!e.0.starts_with("POSS_")))
}
fn derived(p:&Parsed)->bool{p.2.iter().any(|e|e.1!="-")}
fn margin(scores:&[[f64;3]],selected:usize,group:&[usize],column:usize)->f64{
    if group.is_empty(){return 0.0;}
    let rival=maximum(group.iter().map(|&j|scores[j][column]));
    (scores[selected][column]-rival).clamp(-20.0,20.0)
}
fn entropy(values:impl Iterator<Item=f64>)->f64{let mut sum=0.0;for p in values{sum+=p*math::log(p.max(1e-300));}-sum}
fn evidence(paths:&[Parsed],scores:&[[f64;3]],selected:usize)->FeatureMap{
    let chosen=&paths[selected];let others:Vec<usize>=(0..paths.len()).filter(|&j|j!=selected).collect();
    let same:Vec<usize>=others.iter().copied().filter(|&j|root_eq(&paths[j],chosen)).collect();
    let other:Vec<usize>=others.iter().copied().filter(|&j|!root_eq(&paths[j],chosen)).collect();
    let role:Vec<usize>=others.iter().copied().filter(|&j|frame_eq(&paths[j],chosen)).collect();
    let peak=maximum(scores.iter().map(|s|s[0]));
    let ex:Vec<f64>=scores.iter().map(|s|math::exp(s[0]-peak)).collect();let mut total=0.0;for v in &ex{total+=*v;}
    let probs:Vec<f64>=ex.iter().map(|v|v/total).collect();
    // Python root dictionaries preserve insertion order of sorted semantic keys.
    let mut roots:Vec<(usize,f64)>=Vec::new();
    for(j,p)in probs.iter().enumerate(){if let Some((_,mass))=roots.iter_mut().find(|(old,_)|root_eq(&paths[*old],&paths[j])){*mass+=*p;}else{roots.push((j,*p));}}
    let best=|column:usize|{let mut at=0;for j in 1..scores.len(){if scores[j][column]>scores[at][column]{at=j;}}at};
    let local=best(1);let context=best(2);
    let mass=roots.iter().find(|(j,_)|root_eq(&paths[*j],chosen)).unwrap().1;
    let mut f:FeatureMap=vec![
        ("ev_bias".into(),1.0),("ev_local_margin".into(),margin(scores,selected,&others,1)),("ev_context_margin".into(),margin(scores,selected,&others,2)),
        ("ev_local_supports_selected".into(),flag(local==selected)),("ev_context_supports_selected".into(),flag(context==selected)),("ev_local_context_agree".into(),flag(local==context)),
        ("ev_has_role_competition".into(),flag(!role.is_empty())),("ev_has_other_root".into(),flag(!other.is_empty())),("ev_root_count".into(),math::log1p(roots.len()as f64)),
        ("ev_selected_root_mass".into(),mass),("ev_path_entropy".into(),entropy(probs.iter().copied())/math::log(paths.len()as f64).max(1.0)),
        ("ev_root_entropy".into(),entropy(roots.iter().map(|r|r.1))/math::log(roots.len()as f64).max(1.0)),
        ("ev_derivation_competition".into(),flag(!other.is_empty()&&(derived(chosen)||other.iter().any(|&j|derived(&paths[j])))))
    ];
    for(name,group)in [("same_root",&same),("other_root",&other),("role",&role)]{for(column,label)in ["total","local","context"].iter().enumerate(){f.push((format!("ev_{name}_{label}_margin"),margin(scores,selected,group,column)));}}
    f
}
pub fn rank(words:&[String],index:usize,candidates:&[Candidate],codec:bool,weights:&[f32])->io::Result<Ranked>{
    rank_impl(words,index,candidates,codec,weights,None)
}
pub(crate) fn rank_with_group(words:&[String],index:usize,candidates:&[Candidate],codec:bool,weights:&[f32],group:&features::Group)->io::Result<Ranked>{
    rank_impl(words,index,candidates,codec,weights,Some(group))
}
fn rank_impl(words:&[String],index:usize,candidates:&[Candidate],codec:bool,weights:&[f32],group:Option<&features::Group>)->io::Result<Ranked>{
    if index>=words.len(){return Err(io::Error::other("word index"));}
    let mut unique=std::collections::BTreeMap::<&str,usize>::new();
    for(j,c)in candidates.iter().enumerate(){
        let p=(codec&&c.encodable,c.preference.as_str());
        if let Some(&old)=unique.get(c.key.as_str()){
            let old=&candidates[old];
            if p>(codec&&old.encodable,old.preference.as_str()){unique.insert(&c.key,j);}
        }else{unique.insert(&c.key,j);}
    }
    let prepared=match group{Some(group)=>features::prepare_group_at(group,index)?,None=>features::prepare(words,index)?};
    let mut ordered=Vec::new();let mut paths=Vec::new();let mut scores=Vec::new();
    for &j in unique.values(){
        let c=&candidates[j];let parsed=features::path(&c.key)?;
        let score=if let Some(s)=c.forced{s}else{
            let ids=features::indices_prepared(&prepared,&parsed)?;
            let values:Vec<f32>=ids.iter().map(|&x|weights[x as usize]).collect();let split=ids.partition_point(|&x|x<524288);
            [numeric::sum(&values)as f64,numeric::sum(&values[..split])as f64,numeric::sum(&values[split..])as f64]
        };
        if !score.iter().all(|v|v.is_finite()){return Err(io::Error::other("finite score required"));}
        ordered.push((j,score));paths.push(parsed);scores.push(score);
    }
    if ordered.is_empty(){return Ok(Ranked{ordered,selected:None,margin:None,probability:0.0,evidence:Vec::new(),conflicts:Vec::new()});}
    let mut order:Vec<usize>=(0..ordered.len()).collect();order.sort_by(|&a,&b|scores[b][0].partial_cmp(&scores[a][0]).unwrap().then(a.cmp(&b)));
    let top=order[0];let selected=ordered[top].0;let peak=scores[top][0];let ex:Vec<f64>=scores.iter().map(|s|math::exp(s[0]-peak)).collect();
    let mut total=0.0;for v in &ex{total+=*v;}let probability=ex[top]/total;
    let gap=if order.len()>1{Some(peak-scores[order[1]][0])}else{None};
    let ev=evidence(&paths,&scores,top);
    let mut conflicts=std::collections::BTreeMap::new();
    if candidates[selected].flags&4!=0{
        let raw=&words[index];let quotes:Vec<usize>=raw.char_indices().filter(|(_,c)|matches!(c,'\''|'’')).map(|(i,_)|i).collect();
        if quotes.len()==1{
            let prefix=&raw[..quotes[0]];
            for(j,c)in candidates.iter().enumerate(){
                let p=features::path(&c.key)?;
                if p.1!="PROPN" || p.0==paths[top].0 || c.flags&2!=0 || c.flags&8==0 || c.first_surface!=prefix || (codec&&!c.encodable){continue;}
                conflicts.insert(c.key.as_str(),j);
            }
        }
    }
    Ok(Ranked{ordered,selected:Some(selected),margin:gap,probability,evidence:ev,conflicts:conflicts.values().copied().collect()})
}
