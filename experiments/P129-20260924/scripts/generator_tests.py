from common import *
from dataset import episodes,questions,PEOPLE,OBJECTS,ORDERS
import collections
def main():
 used=set();seen_context=set();splitcounts={};labelcounts=collections.Counter()
 held_words={p[0] for p in PEOPLE[12:]}|{o[0] for oo in OBJECTS.values() for o in oo[3:]}
 for split,n in config()["contexts"].items():
  count=0
  for ep in episodes(split,n,used):
   assert ep["context"] not in seen_context
   seen_context.add(ep["context"])
   for role,t,q,answer,choices in questions(ep):
    assert len(set(choices))==4 and answer in choices
    assert ep["events"][t][role]==answer or (ep["events"][t][role] is None and answer=="Belirtilmedi")
    if split=="train":
     assert not held_words.intersection(choices)
     assert all(e["subject"] not in held_words and e["object"] not in held_words and e["owner"] not in held_words for e in ep["events"])
    count+=1;labelcounts[(split,choices.index(answer))]+=1
  assert count==3*n;splitcounts[split]=count
 save(BASE/"tests/generator.json",dict(status="PASS",counts=splitcounts,unique_episodes=len(used),unique_contexts=len(seen_context),
  lexical_targets_and_distractors_disjoint=True,correct_answer_in_unique_four_choices=True,
  label_counts={str(k):v for k,v in labelcounts.items()},main_training_started=False))
 log("GENERATOR PASS "+str(splitcounts))
if __name__=="__main__":main()
