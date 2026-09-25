//! Frozen P21 physical projection, functional paths, annotations and typed filtering.
use std::{collections::BTreeMap, io, path::Path};
use crate::{json::{self,V,s,n},obj,rule_data::{Row,ROWS},rule_values::{Ctx,Val},tables::Table,lexicon::Store,surface,search};
fn normal(p:&str)->&str { match p {"NOMINALIZED"=>"NOUN","CCONJ"|"SCONJ"=>"CONJ",_=>p} }
fn one(s:&str,xs:&[&str])->bool { xs.contains(&s) }
fn prefixed(s:&str,xs:&[&str])->bool { xs.iter().any(|p|s.starts_with(p)) }
fn chars(s:&str)->usize { s.chars().count() }
fn slice(s:&str,start:usize,end:usize)->String { s.chars().skip(start).take(end-start).collect() }
fn events_value(events:&[(String,String)])->V { V::Array(events.iter().map(|(m,p)|V::Array(vec![s(m),s(p)])).collect()) }
fn make_path(root:&str,rp:&str,events:&[(String,String)],fp:&str)->V {
    let root=crate::unicode::lower(root);let ev=events_value(events);
    let key=V::Array(vec![s(&root),s(rp),ev.clone(),s(fp)]).dump();
    obj!("root":s(root),"root_pos":s(rp),"events":ev,"final_pos":s(fp),"key":s(key))
}
fn validate(a:&V,row_map:&BTreeMap<&str,usize>)->io::Result<()> {
    let ids=a.get("record_ids").array();let mids=a.get("morpheme_ids").array();let trace=a.get("realization_trace").array();
    if ids.len()!=mids.len()||ids.len()!=trace.len(){return Err(json::err("SCHEMA_PATH_LENGTH"));}
    for (i,((rid,mid),step)) in ids.iter().zip(mids).zip(trace).enumerate() {
        if !row_map.contains_key(rid.text())||step.get("record_id")!=rid||step.get("morpheme_id")!=mid{return Err(json::err("SCHEMA_RECORD_REFERENCE"));}
        if i>0&&step.get("before")!=trace[i-1].get("after"){return Err(json::err("SCHEMA_BROKEN_TRACE"));}
        if format!("{}{}",step.get("realized_stem").text(),step.get("suffix").text())!=step.get("after").text(){return Err(json::err("SCHEMA_REALIZATION"));}
    }
    if trace.last().is_some_and(|last|last.get("after")!=a.get("surface")){return Err(json::err("SCHEMA_FINAL_SURFACE"));}Ok(())
}
fn project(a:&V,raw:&str)->Option<Vec<V>> {
    let target=crate::unicode::lower(raw);
    if target!=a.get("surface").text()||chars(&target)!=chars(raw){return None;}
    let trace=a.get("realization_trace").array();
    let root=trace.first().map_or(target.as_str(),|t|t.get("before").text());
    let mut pieces=vec![obj!("kind":s("ROOT"),"surface":s(root),"lexeme_id":a.get("lexeme_id").clone(),"lemma":a.get("lemma").clone(),"root_pos":a.get("root_pos").clone())];
    for ((rid,mid),step) in a.get("record_ids").array().iter().zip(a.get("morpheme_ids").array()).zip(trace) {
        let before:String=pieces.iter().map(|p|p.get("surface").text()).collect();
        if before!=step.get("before").text(){return None;}
        let stem=step.get("realized_stem").text();
        if stem!=before {
            if !step.get("rules").truthy(){return None;}
            let common=before.chars().zip(stem.chars()).take_while(|(a,b)|a==b).count();
            let owner=pieces.iter().rposition(|p|!p.get("surface").text().is_empty())?;
            let start=pieces[..owner].iter().map(|p|chars(p.get("surface").text())).sum();
            if common<start{return None;}
            pieces[owner].set("surface",s(slice(stem,start,chars(stem))));
            pieces[owner].set("realization_rules",step.get("rules").clone());
        }
        pieces.push(obj!("kind":s("AFFIX"),"record_id":rid.clone(),"morpheme_id":mid.clone(),"surface":step.get("suffix").clone()));
    }
    if pieces.iter().map(|p|p.get("surface").text()).collect::<String>()!=target||pieces[0].get("surface").text().is_empty(){return None;}
    let mut cursor=0;
    for p in &mut pieces {
        let size=chars(p.get("surface").text());p.set("surface",s(slice(raw,cursor,cursor+size)));cursor+=size;
        let keys=if p.get("kind").text()=="ROOT" {vec![p.get("lexeme_id").clone(),p.get("surface").clone()]}
                 else {vec![p.get("record_id").clone(),p.get("morpheme_id").clone(),p.get("surface").clone()]};
        p.set("key",s(V::Array(keys).dump()));
    }
    if cursor==chars(raw){Some(pieces)}else{None}
}
fn functional(mids:&[V],i:usize)->&str {
    let mid=mids[i].text();if mid=="ABILITY_NEG_BASE"&&mids.get(i+1).is_some_and(|m|m.text()=="POLARITY_NEG"){"ABILITY"}else{mid}
}
fn native_paths(a:&V,raw:&str,row_map:&BTreeMap<&str,usize>)->io::Result<Vec<V>> {
#[cfg(candidate_profile)] let _p112_span=crate::candidate_profile::Span::enter(crate::candidate_profile::PROJECT_PATHS);

    validate(a,row_map)?;let Some(parts)=project(a,raw)else{return Ok(Vec::new());};
    let rp=normal(a.get("root_pos").text());let mut final_pos=normal(a.get("output_pos").text());
    let mut states:Vec<(String,Vec<(String,String)>)>=vec![(rp.into(),Vec::new())];
    let mids=a.get("morpheme_ids").array();
    for (index,rid) in a.get("record_ids").array().iter().enumerate() {
        let mid=functional(mids,index);let row:&Row=&ROWS[row_map[rid.text()]];let mut updated=Vec::new();
        for (mut pos,mut ev) in states {
            let part_poss=pos=="ADJ"&&final_pos=="ADJ"&&mid.starts_with("POSS_")&&mids[..index].iter().any(|m|m.text().starts_with("PART_"));
            if one(&pos,&["ADJ","NUM"])&&prefixed(mid,&["NUMBER_","POSS_","CASE_"])&&!part_poss {ev.push(("ZERO_NOUN".into(),"NOUN".into()));pos="NOUN".into();}
            if mid.starts_with("COP_") {
                let target=if mid=="COP_WHILE"{"ADV"}else{"VERB"};let boundary=if pos!="VERB"||one(mid,&["COP_PRESENT","COP_GENERAL","COP_WHILE"]){target}else{"-"};
                ev.push((mid.into(),boundary.into()));updated.push((target.into(),ev));continue;
            }
            if mid.starts_with("VOICE_")||one(row.class,&["ybE","bvE"]) {ev.push((mid.into(),"VERB".into()));updated.push(("VERB".into(),ev));continue;}
            let targets:Vec<&str>=if row.family=="asif"&&mid=="CONV_CASINA" {vec!["ADJ"]}
                else if mid.starts_with("PART_"){vec!["ADJ","NOUN"]}
                else if mid.starts_with("CONV_"){vec!["ADV"]}
                else if one(mid,&["INF_MAK","VN_MA","VN_IS"]){vec!["NOUN"]}
                else if one(row.class,&["atE","ffE","fiE","fsE","ifE","iiE","isE","kcE","sdE","sfE","siE","syE","ypE","zyE"]){
                    if row.class=="kcE"{vec![&pos]}else{let mut ts:Vec<_>=row.output.iter().filter(|p|one(p,&["NOUN","NOMINALIZED","ADJ","ADV","VERB","PRON","NUM","PROPN"])).map(|p|normal(p)).collect();ts.sort();ts.dedup();ts}
                }else{ev.push((mid.into(),"-".into()));updated.push((pos,ev));continue;};
            for target in targets {let mut next=ev.clone();next.push((mid.into(),target.into()));updated.push((target.into(),next));}
        }
        states=updated;
    }
    if mids.iter().any(|m|m.text().starts_with("COP_")&&m.text()!="COP_WHILE"){final_pos="VERB";}
    // A Python dictionary replaces the value without moving its first insertion position.
    let mut result:Vec<V>=Vec::new();
    for (pos,ev) in states {
        if pos!=final_pos{continue;}
        let mut path=make_path(a.get("lemma").text(),rp,&ev,final_pos);
        path.set("analysis_id",a.get("analysis_id").clone());path.set("parts",V::Array(parts.clone()));
        path.set("subtype_scope",s("NOT_IN_NATIVE_BRIDGE_KEY"));path.set("boundary_scope",s("TRACE_SURFACES_VALIDATED_NOT_CORPUS_BOUNDARY_GOLD"));
        if let Some(old)=result.iter_mut().find(|p|p.get("key")==path.get("key")){*old=path;}else{result.push(path);}
    }
    Ok(result)
}
fn quote_slot(parts:&[V],at:usize)->Option<usize> {
    let mut cursor=0;for (i,p) in parts.iter().enumerate(){
        if p.get("kind").text()=="AFFIX"&&!prefixed(p.get("morpheme_id").text(),&["NUMBER_","POSS_"]){return None;}
        cursor+=chars(p.get("surface").text());if cursor>at{return None;}if cursor==at{return Some(i+1);}
    }None
}
pub struct Provider {
    pub lex:Store,pub config:surface::Config,metadata:Table,rows:BTreeMap<&'static str,usize>,
}
impl Provider {
    pub fn open(data:&Path)->io::Result<Self>{Ok(Self{lex:Store::open(&data.join("lex"))?,config:surface::Config::open(&data.join("surface"))?,metadata:Table::open(&data.join("projection.bin"))?,rows:ROWS.iter().enumerate().map(|(i,r)|(r.id,i)).collect()})}
    fn annotation(&mut self,kind:&str,id:&str)->io::Result<V>{
#[cfg(candidate_profile)] let _p112_span=crate::candidate_profile::Span::enter(crate::candidate_profile::ANNOTATION);
match crate::p112_expr!(ANNOTATION_LOOKUP, self.metadata.get(&format!("{kind}\0{id}")))?{None=>Ok(V::Null),Some(bytes)=>crate::p112_expr!(ANNOTATION_PARSE, json::parse(std::str::from_utf8(&bytes).map_err(|_|json::err("metadata UTF8"))?))}}
    pub fn candidates(&mut self,raw:&str)->io::Result<V> {
#[cfg(candidate_profile)] let _p112_span=crate::candidate_profile::Span::enter(crate::candidate_profile::PROVIDER);

        let (output,_stats)=search::search(raw,[20000,256,20],&mut self.lex,&mut self.config)?;
        let output=crate::p112_expr!(PROVIDER_SEARCH_PARSE, json::parse(&output))?;crate::p112_event!(E_NATIVE_ANALYSES, output.get("analyses").array().len());let mut hypotheses=Vec::new();
        let quotes:Vec<_>=raw.chars().enumerate().filter(|(_,c)|matches!(c,'\''|'’')).collect();
        let mut annotations:BTreeMap<String,[V;4]>=BTreeMap::new();
        for a in output.get("analyses").array() {
            let mut projected=raw.to_string();
            if !quotes.is_empty(){if quotes.len()!=1||a.get("root_pos").text()!="PROPN"{continue;}projected=raw.chars().enumerate().filter(|(i,_)|*i!=quotes[0].0).map(|(_,c)|c).collect();}
            let id=a.get("lexeme_id").text();
            if !annotations.contains_key(id){annotations.insert(id.into(),[self.annotation("compounds",id)?,self.annotation("compound_stems",id)?,self.annotation("spelling_aliases",id)?,self.annotation("name_readings",id)?]);}
            let [compound,stem,spelling,reading]=&annotations[id];
            for mut path in native_paths(a,&projected,&self.rows)? {
                let mut parts=path.get("parts").array().to_vec();
                if !quotes.is_empty(){let (at,c)=quotes[0];let Some(slot)=quote_slot(&parts,at)else{continue;};if slot==parts.len(){continue;}
                    if reading.get("kind")==&s("INFLECTED_TITLE")&&!parts[..slot].iter().any(|p|p.get("kind").text()=="AFFIX"&&!p.get("surface").text().is_empty()){continue;}
                    parts.insert(slot,obj!("kind":s("LAYOUT"),"surface":s(c.to_string())));
                }
                path.set("parts",V::Array(parts));
                if compound.truthy(){
                    let mut events=vec![("POSS_3_SING".into(),"-".into())];events.extend(path.get("events").array().iter().map(|v|(v.array()[0].text().into(),v.array()[1].text().into())));
                    let core=make_path(path.get("root").text(),path.get("root_pos").text(),&events,path.get("final_pos").text());
                    for (key,value) in core.fields(){path.set(key,value.clone());}
                    path.set("lexical_structure",compound.clone());path.set("inherited_events",V::Array(vec![obj!("event":s("POSS_3_SING"),"realized_in":s("ROOT_ID"))]));
                }
                if stem.truthy(){path.set("lexical_structure",stem.clone());}if spelling.truthy(){path.set("spelling_provenance",spelling.clone());}if reading.truthy(){path.set("name_reading_provenance",reading.clone());}
                if path.get("parts").array().iter().map(|p|p.get("surface").text()).collect::<String>()!=raw{return Err(json::err("P11_PROVIDER_SURFACE_MISMATCH"));}
                path.set("registry_analysis",obj!("analysis_id":a.get("analysis_id").clone(),"lexeme_id":a.get("lexeme_id").clone(),"morpheme_ids":a.get("morpheme_ids").clone(),"record_ids":a.get("record_ids").clone(),"features":a.get("features").clone()));
                hypotheses.push(path);
            }
        }
        #[cfg(candidate_profile)] let _p112_filter=crate::candidate_profile::Span::enter(crate::candidate_profile::PROVIDER_FILTER);
        let before=hypotheses.len();crate::p112_event!(E_HYPOTHESES_BEFORE_FILTER, before);let mut cache:BTreeMap<(String,String,bool),V>=BTreeMap::new();let mut valid=Vec::new();
        for path in hypotheses {
            let a=path.get("registry_analysis");let key=(a.get("analysis_id").text().into(),path.get("final_pos").text().into(),path.get("lexical_structure").truthy());
            if !cache.contains_key(&key){
                let ids:Vec<usize>=a.get("record_ids").array().iter().map(|id|self.rows[id.text()]).collect();
                let mids:Vec<String>=a.get("morpheme_ids").array().iter().map(|v|v.text().into()).collect();
                let feats:Ctx=a.get("features").fields().iter().map(|(k,v)|(k.clone().into(),Val::s(v.text()))).collect();
                let (events,_)=search::replay(raw,a.get("lexeme_id").text(),path.get("final_pos").text(),path.get("inherited_events").truthy(),&ids,&mids,&feats,&mut self.lex,&mut self.config)?;
                cache.insert(key.clone(),crate::p112_expr!(REPLAY_PARSE, json::parse(&events))?);
            }
            if cache[&key].array().contains(path.get("events")){valid.push(path);}
        }
        crate::p112_event!(E_FINAL_PATHS, valid.len());
#[cfg(candidate_profile)] drop(_p112_filter);
        Ok(obj!("raw":s(raw),"search_complete":output.get("search_complete").clone(),"native_analyses":n(output.get("analyses").array().len()),
            "unrealizable_interpretations_removed":n(before-valid.len()),"native_record_sequences_replayed":V::Bool(true),
            "provider_version":s("P11-TYPED-PATH-PROVIDER-1"),"paths":V::Array(valid)))
    }
}
