//! One-process P21-compatible inference. Frozen model arithmetic is reused unchanged.
use std::{collections::VecDeque, fs::File, io::{self,Read}, path::Path, time::Instant, sync::Arc};
use crate::{features,json::{self,V,s,n,f},obj,projection::Provider,raw,boundary,codec::{self,Codec,Part},ranking::{self,Candidate},gate,tables::{Table,Frequencies}};
struct Prepared { candidates:Vec<Candidate>,search_complete:bool }
struct Cached { raw:Box<str>, serialized:Box<str>, charge:usize, prepared:Option<Arc<Prepared>>, prepared_charge:usize }
pub struct Runtime {
    pub provider:Provider, codec:Codec, weights:Vec<f32>, frequencies:Frequencies,
    cache:VecDeque<Cached>,cache_bytes:usize,cache_limit:usize,pub cache_hits:u64,pub cache_misses:u64,prepared_hits:u64,prepared_misses:u64,
    pub phase_ns:[u128;5],pub load_seconds:f64,
}
fn ids_value(ids:&[u32])->V { V::Array(ids.iter().map(|v|n(*v as usize)).collect()) }
fn flags(p:&V)->u32 {
    (p.get("lexical_structure").truthy() as u32) | ((p.get("name_reading_provenance").truthy() as u32)<<1)
    | ((p.get("name_reading_provenance").get("kind")==&s("INFLECTED_TITLE")) as u32)<<2 | ((p.get("parts").truthy() as u32)<<3)
}
fn parts(p:&V)->Vec<Part>{parts_array(p.get("parts").array())}
fn parts_array(values:&[V])->Vec<Part>{values.iter().map(|v|Part{kind:v.get("kind").text().into(),key:if v.has("key"){v.get("key").text().into()}else{String::new()},surface:v.get("surface").text().into()}).collect()}
fn admission(a:&gate::Admission)->V {
    let mut out=obj!("accepted":V::Bool(a.accepted),"reason":s(a.reason),"risk_score":a.risk.map_or(V::Null,f),"calibrated_probability":V::Null);
    if a.risk.is_some(){out.set("threshold",a.threshold.map_or(V::Null,f));out.set("score_target",s("SEMI_AUTOMATIC_CANONICAL_FUNCTIONAL_PATH_AGREEMENT"));}out
}
impl Runtime {
    pub fn open(data:&Path,cache_limit:usize)->io::Result<Self>{
        let started=Instant::now();crate::integrity::verify(data)?;let mut file=File::open(data.join("weights-f32.bin"))?;
        if !cfg!(target_endian="little")||file.metadata()?.len()!=4194304{return Err(json::err("frozen f32 weight dimensions"));}
        let mut weights=vec![0.0_f32;1048576];
        let bytes=unsafe{std::slice::from_raw_parts_mut(weights.as_mut_ptr() as *mut u8,4194304)};file.read_exact(bytes)?;
        if !weights.iter().all(|v|v.is_finite()){return Err(json::err("nonfinite weights"));}
        let codec=Codec::open(&data.join("codec"))?;let provider=Provider::open(data)?;
        let frequencies=Frequencies{words:Table::open(&data.join("freq/words.bin"))?,paths:Table::open(&data.join("freq/paths.bin"))?};
        Ok(Self{provider,codec,weights,frequencies,cache:VecDeque::new(),cache_bytes:0,cache_limit,cache_hits:0,cache_misses:0,prepared_hits:0,prepared_misses:0,phase_ns:[0;5],load_seconds:started.elapsed().as_secs_f64()})
    }
    pub fn clear_cache(&mut self){self.cache.clear();self.cache.shrink_to_fit();self.cache_bytes=0;}
    pub fn cache_info(&self)->V {obj!("serialized_bytes":n(self.cache.iter().map(|e|e.serialized.len()).sum()),"prepared_payload_bytes":n(self.cache.iter().map(|e|e.prepared_charge).sum()),"prepared_entries":n(self.cache.iter().filter(|e|e.prepared.is_some()).count()),"prepared_hits":n(self.prepared_hits as usize),"prepared_misses":n(self.prepared_misses as usize),"payload_bytes":n(self.cache_bytes),"payload_limit":n(self.cache_limit),"entries":n(self.cache.len()),"hits":n(self.cache_hits as usize),"misses":n(self.cache_misses as usize))}
    pub fn candidates(&mut self,raw:&str)->io::Result<V>{
#[cfg(candidate_profile)] let _p112_span=crate::candidate_profile::Span::enter(crate::candidate_profile::CANDIDATE_CACHE);

        if let Some(i)=crate::p112_expr!(SERIALIZED_SCAN, self.cache.iter().position(|e|e.raw.as_ref()==raw)){
            let cached=self.cache.remove(i).unwrap();let result=crate::p112_expr!(SERIALIZED_PARSE, json::parse(&cached.serialized))?;self.cache.push_back(cached);self.cache_hits+=1;crate::p112_event!(E_SERIALIZED_HITS, 1);return Ok(result);
        }
        self.cache_misses+=1;crate::p112_event!(E_PROVIDER_MISSES, 1);let result=self.provider.candidates(raw)?;
        if self.cache_limit>0 {
#[cfg(candidate_profile)] let _p112_span=crate::candidate_profile::Span::enter(crate::candidate_profile::CACHE_ADMISSION);

            let serialized=crate::p112_expr!(CACHE_DUMP, result.dump().into_boxed_str());let key:Box<str>=raw.into();let charge=key.len()+serialized.len()+std::mem::size_of::<Cached>();
            if charge<=self.cache_limit {
                while self.cache_bytes+charge>self.cache_limit||self.cache.len()>=1024{let old=self.cache.pop_front().unwrap();self.cache_bytes-=old.charge;crate::p112_event!(E_CACHE_EVICTIONS, 1);}
                crate::p112_event!(E_CACHE_INSERTIONS, 1);self.cache_bytes+=charge;self.cache.push_back(Cached{raw:key,serialized,charge,prepared:None,prepared_charge:0});
            }else{crate::p112_event!(E_OVERSIZE_SKIPS, 1);}
        }
        Ok(result)
    }
    // Encode-only cache hits need no JSON metadata. Full/audit callers still
    // parse the original serialized value and obtain the same complete result.
    fn cached_prepared(&mut self,raw:&str)->Option<Arc<Prepared>>{
#[cfg(candidate_profile)] let _p112_span=crate::candidate_profile::Span::enter(crate::candidate_profile::PREPARED_CACHE);

        let i=self.cache.iter().position(|e|e.raw.as_ref()==raw)?;
        let prepared=Arc::clone(self.cache[i].prepared.as_ref()?);
        let entry=self.cache.remove(i).unwrap();self.cache.push_back(entry);
        self.cache_hits+=1;self.prepared_hits+=1;crate::p112_event!(E_PREPARED_FAST_HITS, 1);Some(prepared)
    }
    // Public candidates() still only returns the same serialized candidate data.
    // This lazy step runs exactly where process() already checked the codec.
    fn prepared_candidates(&mut self,raw:&str,paths:&[V],search_complete:bool)->io::Result<Arc<Prepared>>{
        // candidates(raw) has just moved or inserted this raw key at the LRU back.
        if let Some(entry)=self.cache.back().filter(|e|e.raw.as_ref()==raw){
            if let Some(prepared)=&entry.prepared{
                self.prepared_hits+=1;return Ok(Arc::clone(prepared));
            }
        }
        self.prepared_misses+=1;
        let mut candidates=Vec::with_capacity(paths.len());
                for path in paths {
                    let pp=parts(path);let encodable=self.codec.encodable(&pp)?;
                    candidates.push(Candidate{key:path.get("key").text().into(),preference:path.get("parts").dump_with_spaces(true),encodable,flags:flags(path),
                        first_surface:path.get("parts").array().first().map_or("",|p|p.get("surface").text()).into(),lexeme_id:path.get("registry_analysis").get("lexeme_id").text().into(),forced:None});

                }

        // Count vector capacity, owned String capacities, and the Arc allocation.
        // Inline Candidate fields are already covered by size_of::<Candidate>().
        let extra=std::mem::size_of::<Prepared>()+2*std::mem::size_of::<usize>()
            +candidates.capacity()*std::mem::size_of::<Candidate>()
            +candidates.iter().map(|c|c.key.capacity()+c.preference.capacity()+c.first_surface.capacity()+c.lexeme_id.capacity()).sum::<usize>();
        let prepared=Arc::new(Prepared{candidates,search_complete});
        if self.cache.back().is_some_and(|e|e.raw.as_ref()==raw&&e.charge+extra<=self.cache_limit){
            let mut entry=self.cache.pop_back().unwrap();self.cache_bytes-=entry.charge;
            entry.charge+=extra;entry.prepared_charge=extra;entry.prepared=Some(Arc::clone(&prepared));
            while self.cache_bytes+entry.charge>self.cache_limit{
                let old=self.cache.pop_front().unwrap();self.cache_bytes-=old.charge;
            }
            self.cache_bytes+=entry.charge;self.cache.push_back(entry);
        }
        // If this prepared entry is oversized, keep only its ordinary JSON cache.
        // Ranking and all context-dependent decisions still run on every request.
        Ok(prepared)
    }
    pub fn decode(&mut self,ids:&[u32])->io::Result<String>{
        let bytes=self.codec.decode(ids)?.ok_or_else(||json::err("invalid token ID"))?;
        String::from_utf8(bytes).map_err(|_|json::err("token sequence is not valid UTF8; use decode_bytes"))
    }
    pub fn decode_bytes(&mut self,ids:&[u32])->io::Result<Vec<u8>>{self.codec.decode(ids)?.ok_or_else(||json::err("invalid token ID"))}
    pub fn analyze(&mut self,text:&str,audit:bool)->io::Result<(V,V)>{let (result,trace,_)=self.process(text,audit,true)?;Ok((result,trace))}
    pub fn encode(&mut self,text:&str)->io::Result<Vec<u32>>{Ok(self.process(text,false,false)?.2)}
    fn process(&mut self,text:&str,audit:bool,full:bool)->io::Result<(V,V,Vec<u32>)>{
        let time=Instant::now();let plan=raw::prepare(text)?;
        let units:Vec<boundary::Unit>=plan.units.iter().map(|u|boundary::Unit{start:u.span.start as usize,end:u.span.end as usize,kind:u.span.kind}).collect();
        let boundaries=boundary::boundaries(text,&units)?;
        let words:Vec<Vec<String>>=plan.groups.iter().map(|group|group.iter().map(|sp|plan.chars[sp.start as usize..sp.end as usize].iter().collect()).collect()).collect();
        let mut contexts:Vec<Option<features::Group>>=words.iter().map(|_|None).collect();
        self.phase_ns[0]+=time.elapsed().as_nanos();
        let mut ids=Vec::new();let mut spans=Vec::new();let mut trace=Vec::new();
        // Each decision sees only the original text group, never neighboring decisions.
        for (j,u) in plan.units.iter().enumerate(){
            let raw:String=plan.chars[u.span.start as usize..u.span.end as usize].iter().collect();
            let mut decision=V::Null;let mut ad=V::Null;let mut chosen=V::Null;let mut edge=V::Null;
            let mut selected_prepared:Option<(Arc<Prepared>,usize)>=None;
            let mut accepted=false;
            if matches!(u.span.kind,1|2){
                let time=Instant::now();
#[cfg(candidate_profile)] let _p112_span=crate::candidate_profile::Span::enter(crate::candidate_profile::ROOT);
let hot=if !full&&!audit{self.cached_prepared(&raw)}else{None};
                let native=if hot.is_some(){V::Null}else{self.candidates(&raw)?};
#[cfg(candidate_profile)] drop(_p112_span);
self.phase_ns[1]+=time.elapsed().as_nanos();
                let time=Instant::now();let paths=if native==V::Null{&[][..]}else{native.get("paths").array()};
                let prepared=match hot{Some(p)=>p,None=>self.prepared_candidates(&raw,paths,native.get("search_complete").boolean())?};
                let candidates=&prepared.candidates;
                let gi=u.group as usize;
                let context=contexts[gi].get_or_insert_with(||features::group(&words[gi]));
                let ranked=ranking::rank_with_group(&words[gi],u.index as usize,&candidates,true,&self.weights,context)?;
                let mut score_map=std::collections::BTreeMap::new();
                if audit {for (i,scores) in &ranked.ordered{score_map.insert(candidates[*i].key.clone(),V::Array(scores.iter().copied().map(f).collect()));}}
                if let Some(selected)=ranked.selected {
                    selected_prepared=Some((Arc::clone(&prepared),selected));
                    if full||audit {
                    chosen=paths[selected].clone();let score=ranked.ordered.iter().find(|(i,_)|*i==selected).unwrap().1[0];
                    let evidence=V::Object(ranked.evidence.iter().map(|(k,v)|(k.clone(),f(*v))).collect());
                    let conflicts=V::Array(ranked.conflicts.iter().map(|i|obj!("key":s(&candidates[*i].key),"lexeme_id":s(&candidates[*i].lexeme_id))).collect());
                    decision=obj!("path":chosen.clone(),"score":f(score),"margin":ranked.margin.map_or(V::Null,f),"model_probability":f(ranked.probability),"calibrated_probability":V::Null,
                        "candidate_paths":n(ranked.ordered.len()),"context_evidence":obj!("version":s("P18-OBSERVABLE-PATH-COMPETITION-1"),"features":evidence),"known_name_ambiguity":obj!("veto":V::Bool(!ranked.conflicts.is_empty()),"literal_name_candidates":conflicts,"version":s("P11S-KNOWN-NAME-AMBIGUITY-1"))); }
                }
                self.phase_ns[2]+=time.elapsed().as_nanos();let time=Instant::now();
                let gate_decision=ranked.selected.map(|i|gate::Decision{key:candidates[i].key.clone(),count:ranked.ordered.len(),margin:ranked.margin,probability:ranked.probability,
                    flags:candidates[i].flags,safety:if ranked.conflicts.is_empty(){1}else{2},evidence:Some(ranked.evidence)});
                let a=gate::decide(&raw,gate_decision.as_ref(),prepared.search_complete,ranked.selected.is_some_and(|i|candidates[i].encodable),&mut self.frequencies)?;
                accepted=a.accepted;
                if full||audit {ad=admission(&a);}
                let b=boundaries.iter().find(|b|b.unit==j).ok_or_else(||json::err("missing word boundary"))?;
                if b.reason!=0 {accepted=false;}
                if full||audit {
                let reason=["P20_SINGLE_WORD_BOUNDARY","P20_UNRESOLVED_ORTHOGRAPHIC_GROUP","P20_UNRESOLVED_ABBREVIATION"][b.reason as usize];
                edge=obj!("allowed":V::Bool(b.reason==0),"reason":s(reason),"group_start":n(b.lo),"group_end":n(b.hi),"morph_members":n(b.members));
                if b.reason!=0 {ad=obj!("accepted":V::Bool(false),"reason":s(reason),"risk_score":V::Null,"calibrated_probability":V::Null);}
                }
                self.phase_ns[3]+=time.elapsed().as_nanos();
                if audit {trace.push(obj!("raw":s(&raw),"candidates":native,"scores":V::Object(score_map),"decision":decision.clone()));}
            }
            let time=Instant::now();let first=ids.len();
            let encoded=if accepted{
                let (prepared,index)=selected_prepared.as_ref().ok_or_else(||json::err("missing selected physical path"))?;
                // preference already stores the exact JSON array of physical parts.
                // Parse only the selected accepted path; full/audit uses its original V.
                let pp=if full||audit{parts(&chosen)}else{
                    let stored=json::parse(&prepared.candidates[*index].preference)?;parts_array(stored.array())
                };
                self.codec.encode_path(&pp,raw.as_bytes())?.map_err(|_|json::err("P11_MORPH_ROUNDTRIP"))?
            }else{codec::encode(raw.as_bytes())};
            if !accepted&&encoded.iter().any(|i|*i<8||*i>=2312){return Err(json::err("BPE ID range"));}
            ids.extend(&encoded);
            if full { spans.push(obj!("start":n(u.span.start as usize),"end":n(u.span.end as usize),"raw":s(raw),"route":s(if accepted{"MORPH"}else{"BPE"}),
                "reason":if ad==V::Null{s(raw::KINDS[u.span.kind as usize])}else{ad.get("reason").clone()},
                "id_start":n(first),"id_end":n(ids.len()),"input_ids":ids_value(&encoded),"accepted_path":if accepted{chosen}else{V::Null},"proposal":decision,"admission":ad,"boundary":edge)); }
            self.phase_ns[4]+=time.elapsed().as_nanos();
        }
        if self.decode_bytes(&ids)?.as_slice()!=text.as_bytes(){return Err(json::err("sentence roundtrip mismatch"));}
        let result=if full {obj!("tokenizer_version":s("S06E-P21-Stable-v1.0.0"),"raw":s(text),"input_ids":ids_value(&ids),"spans":V::Array(spans),"lossless":V::Bool(true),
            "production_selected":V::Bool(true),"vocabulary_size":n(codec::COUNT as usize),"dynamic_ids":V::Bool(false),"morphology_target":s("CANONICAL_FUNCTIONAL_PATH"),"raw_boundary_gold_accuracy":V::Null,
            "release_channel":s("stable"),"selection_basis":s("USER_PINNED_P21"),"a1_contract_id":s("5b91c209c17834816a2c8a07ab70e3a0880ed6e6c1f612c9e2534e4fde2e10b6"))}else{V::Null};
        Ok((result,V::Array(trace),ids))
    }
}
