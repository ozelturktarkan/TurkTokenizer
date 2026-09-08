import unittest
from .numerics import np,matrix,objective


class WeightedPartialLabelTests(unittest.TestCase):
    def data(self,shifts=(0.,0.)):
        rows=[{'features':[{'x':1.},{'y':2.},{'x':-.5,'y':1.}], 'good':[True,False,True], 'offsets':[-80.,0.,-45.]},
              {'features':[{'x':2.},{'y':1.}], 'good':[False,True], 'offsets':[1.,2.]}]
        for row,shift in zip(rows,shifts):row['offsets']=[x+shift for x in row['offsets']]
        return matrix(rows,{'x':0,'y':1})
    def test_gradient_matches_finite_difference(self):
        data=self.data();w=np.asarray([.3,-.6]);weights=np.asarray([.5,1.]);loss,grad=objective(w,data,weights,.01)
        eps=1e-5;numerical=[]
        for i in range(len(w)):
            plus=w.copy();minus=w.copy();plus[i]+=eps;minus[i]-=eps
            numerical.append((objective(plus,data,weights,.01)[0]-objective(minus,data,weights,.01)[0])/(2*eps))
        self.assertTrue(np.isfinite(loss));np.testing.assert_allclose(grad,numerical,atol=1e-7,rtol=1e-6)
    def test_score_shifts_and_weight_scale_leave_loss_unchanged(self):
        w=np.asarray([.3,-.6]);weights=np.asarray([.5,1.])
        x,g=objective(w,self.data(),weights,.01);y,h=objective(w,self.data((1e4,-1e4)),weights*10,.01)
        self.assertAlmostEqual(x,y,places=10);np.testing.assert_allclose(g,h,atol=1e-10)


if __name__=='__main__':unittest.main()
