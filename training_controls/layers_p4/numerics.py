import sys
from bootstrap import ROOT
sys.path[:0]=[str(ROOT/'.deps-s06'),str(ROOT/'.deps-s05six')]
import numpy as np
from scipy.optimize import minimize
from training_controls.a1_epoch.numerics import matrix
from .common import records,require


def objective(w,data,weights,regularization):
    X,starts,ends,good,offsets=data;lengths=ends-starts;scores=offsets+X@w
    maxima=np.maximum.reduceat(scores,starts);ex=np.exp(scores-np.repeat(maxima,lengths));sums=np.add.reduceat(ex,starts)
    masked=np.where(good,scores,-np.inf);gm=np.maximum.reduceat(masked,starts)
    ge=np.where(good,np.exp(masked-np.repeat(gm,lengths)),0.);gs=np.add.reduceat(ge,starts)
    norm=weights/weights.sum();p=ex/np.repeat(sums,lengths);q=ge/np.repeat(gs,lengths)
    loss=float(norm@(maxima+np.log(sums)-gm-np.log(gs))+regularization*(w@w))
    grad=np.asarray(X.T@((p-q)*np.repeat(norm,lengths))).ravel()+2*regularization*w
    return loss,grad


def fit(path,frequencies,config):
    keys=sorted(k for k,n in frequencies.items() if n>=config['minimum_frequency']);vocab={k:i for i,k in enumerate(keys)}
    require(bool(keys),'P4_EMPTY_FEATURE_VOCABULARY');data=matrix(records(path),vocab)
    weights=np.asarray([r.get('weight',1.) for r in records(path)],dtype=float)
    require(len(weights)==len(data[1]) and (weights>0).all(),'P4_INVALID_TRAIN_WEIGHTS')
    initial=np.zeros(len(keys));f=lambda w:objective(w,data,weights,config['regularization'])
    result=minimize(f,initial,jac=True,method='L-BFGS-B',options={'maxiter':config['maxiter'],'ftol':1e-9})
    require(np.isfinite(result.x).all() and result.fun<=f(initial)[0]+1e-9,'P4_FIT_INVALID')
    return {k:float(result.x[i]) for k,i in vocab.items()},{'examples':len(weights),'candidate_rows':len(data[3]),'features':len(keys),
        'initial_loss':f(initial)[0],'final_loss':float(result.fun),'iterations':int(result.nit),
        'optimizer_success':bool(result.success),'optimizer_message':str(result.message)}
