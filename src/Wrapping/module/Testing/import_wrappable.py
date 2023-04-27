import wrapping
from wrapping import vtkWrappable

wrap = vtkWrappable.vtkWrapped()
print (wrap)
assert wrap.GetString() == 'wrapped'
