from measurement import Measurement
from model import Model
#from response_surface import response_surface
from solution import Solution

import numpy as np
import copy
import math
import matplotlib
import matplotlib.pyplot as plt

class Project(object):
    """This is the top level Project class for the MUM-PCE code. 

    :param measurement_list: The list of measurements that will constrain the model
    :param application_list: The list of applications that will be targeted for experimental design
    :param initialize_function: A user-specified function that will read a database of experiments and create the measurement list. Stored in :func:`self.initialize_function`
    :param app_initialize_function: A user-specified function that will read a database of experiments and create the application list. Stored in :func:`self.app_initialize_function`. By default, it is the same as initialize_function
    :param model: The model that will be passed to the initialization function when creating the measurement list
    :param active_parameters: The list of parameters in the model that will be optimized. Normally not defined at project creation.
    :param active_parameter_uncertainties: The uncertainty factors of the active parameters. Normally not defined at project creation.
    :param parameter_uncertainties: The uncertainty factors of all parameters in the model. Normally this is not provided as part of the model and must be specified separately.    
    :param solution: The solution object generated by optimization and uncertainty constraint. Normally not defined at project creation.
    :type measurement_list: list of measurement objects 
    :type initialize_function: function
    :type app_initialize_function: function
    :type model: str
    :type active_parameters: int list
    :type active_parameter_uncertainties: float list
    :type parameter_uncertainties: float list
    :type solution: solution object
    
    A Project object is intended to contain a model, a set of measurements, and a version of that model that has been 
    constrained against those experiments. Note that it is allowed to create a project object without specifying any 
    parameter, instead defining them later.
    
    The Project object acts as a container for the measurment and application lists. Measurements in either list can be accessed by number or by name, that is by calling:
    
    ::
    
       Project[0]
       Project["First experiment's name"]
       
    
    """
    def __init__(self,
                 measurement_list=None,
                 application_list=None,
                 model=None,
                 active_parameters=None,
                 active_parameter_uncertainties=None,
                 parameter_uncertainties=None,
                 initialize_function=None,
                 app_initialize_function=None,
                 solution=None
                ):
        """
        """
        #: The list of measurements that are part of this project
        self.measurement_list = measurement_list
        if measurement_list is None:
            self.measurement_list = []
        
        #: The list of model parameter information. If the measurement list exists when the Project is instantiated, Project will retrive this information from the first measurement.
        self.model_parameter_info = None
        if measurement_list is not None:
            self.model_parameter_info = self.measurement_list[0].model.model_parameter_info
        
        #Inconsistent measurements will be removed from the measurement list and added to this list 
        self.removed_list = []
        
        #Low information measurements will be removed from the measurement list and added to this list
        #They will still contribute to the 
        self.low_information = []
        
        #: The list of applications that will be used for experimental design
        self.application_list = application_list
        if application_list is None:
            self.application_list = []
            for meas in self.application_list:
                meas._status = 'Application'
        
        #: The model for this project, usually this is passed to the initialization function
        self.model = model
        
        #: The list of active parameters. Normally not defined at project creation.
        self.active_parameters = active_parameters
        #: The list of active parameter uncertainties. Normally not defined at project creation.
        self.active_parameter_uncertainties = active_parameter_uncertainties
        
        #: The list of uncertainties for the full model
        self.parameter_uncertainties = parameter_uncertainties
        
        #: A user-specified function that will read a database of experiments and create the measurement list. 
        self.initialize_function = initialize_function
        #: A user-specified function that will read a database of experiments and create the application list. Stored in :func:`self.app_initialize_function`. By default, it is the same as initialize_function
        self.app_initialize_function = app_initialize_function
        if app_initialize_function is None:
            self.app_initialize_function = initialize_function
        
        #: The solution object generated by optimization and uncertainty constraint. Normally not defined at project creation.
        self.solution = solution
        
        return
    
    @property
    def items(self):
        items = []
        for meas_list in [self.measurement_list,self.application_list,self.removed_list,self.low_information]:
            if meas_list is not None:
                items += meas_list
        return items
    
    @property
    def names(self):
        names = {}
        for item in self.items:
            names[item.name] = item
        return names
    
    @property
    def active(self):
        active = []
        for meas_list in [self.measurement_list,self.application_list]:
            if meas_list is not None:
                active += meas_list
        return active
    
    def __len__(self):
        return len(self.items)
    
    def __getitem__(self,x):
        if type(x) is int:
            return self.items[x]
        else:
            try:
                return self.names[x]
            except KeyError:
                print('No measurement with name ' + x)
        
        return #items[x]
    
    def __setitem__(self,key,newmeas):
        if type(newmeas) is mumpce.measurement:
            try:
                self.measurement_list[key] = newmeas
            except IndexError:
                self.application_list[key - len(self.measurement_list)] = newmeas
        else:
            raise(ValueError,'Cannot replace measurement with non-measurement')
        return
    
    def __add__(self,newmeas):
        self._add_measurement(newmeas)
    
    def _add_measurement(self,newmeas):
        if type(newmeas) is mumpce.measurement:
            self.measurement_list += [newmeas]
        else:
            raise(ValueError,'Cannot add non-measurement to measurement list')
    
    def add_application(self,newmeas):
        if type(newmeas) is mumpce.measurement:
            self.application_list += [newmeas]
        else:
            raise(ValueError,'Cannot add non-measurement to application list')        
    
    def __iter__(self):
        return iter(self.items)
        
    def save(self):
        """Saves all measurements that are part of this project to disk. Calls the :func:`save()` function for each measurement
        """
        for meas in self.measurement_list + self.application_list:
            meas.save()
    
    def load(self):
        """Loads all measurements that are part of this project from disk. Calls the :func:`load()` function for each measurement
        """
        for meas in self.measurement_list + self.application_list:
            meas.load()
    
    def find_sensitivity(self):
        """For each measurement in the measurement and application lists, evaluates and stores the sensitivity 
        """
        for meas in self.measurement_list + self.application_list:
            print meas.name
            meas.evaluate_sensitivity()
        return
    
    def set_active_parameters(self):
        """For each measurement in the measurement and application lists, sets the active parameter and parameter uncertainty lists to be the same as the Project's. 
        """
        #Set the active parameter list for all measurements to the main active parameter list for this project
        for meas in self.measurement_list + self.application_list:
            meas.active_parameters = self.active_parameters
            meas.parameter_uncertainties=self.active_parameter_uncertainties
        return
    
    def find_active_parameters(self,sensitivity_cutoff):
        """Determines the active parameters for this project based on the sensitivities of the measurements to the model
        parameters, weighted by the uncertainty factors
        
        :param sensitivity_cutoff: The sensitivity cutoff :math:`S_c`
        :type sensitivity_cutoff: float
                
        .. |br| raw:: html
           
           <br />
        
        |br| For each parameter :math:`i` and measurement :math:`r`, an impact factor :math:`I_{i,r}` is calculated as :math:`I_{i,r} = S_{i,r}  \ln(f_i)` where :math:`S_{i,r}` is the sensitivity of the rth measurement to the ith parameter and :math:`f_i` is the uncertainty factor of the ith parameter.
        
        Active parameters are those such that :math:`I_{i,r} > \max_i(I_{i,r}) S_c`, where :math:`S_c` is the sensitivity cutoff.


        """
        #Create an empty array of the active parameters
        self.active_parameters = np.array([],dtype=int)
        for meas in self.measurement_list:
            print meas.name
            #Create the list of parameters for this measurement
            all_parameters = np.arange(meas.model.number_parameters,dtype=int)
            
            #Check to see if the sensitivity list exists for this measurement
            #If it does not exist, evaluate the sensi
            if meas.sensitivity_list is None:
                meas.evaluate_sensitivity()
                
            impact_factor_list = meas.sensitivity_list * np.log(self.parameter_uncertainties    )
            
            #Get the sensitivities for this measurement
            #computed_val,sensitivity_list = meas.model.sensitivity(perturbation=0.1,parameter_list=all_parameters)
            
            #Find the maximum sensitivity and determine the active parameters for this experiment
            max_sens = abs(impact_factor_list).max()*sensitivity_cutoff
            active_parameters_this = all_parameters[abs(impact_factor_list) > max_sens]
            
            self.active_parameters = np.union1d(self.active_parameters,active_parameters_this)
        self.active_parameter_uncertainties = self.parameter_uncertainties[self.active_parameters]
    
#    active_parameters_reactions += [active_paramters_this]
        return
    
    def optimize_parameters(self):
        pass
    
    def measurement_initialize(self,filename):
        """Calls :func:`self.initialize_function` to create the measurement list.
        
        :param filename: The file containing the experimental database
        :type filename: str
        """
        self.measurement_list = self.initialize_function(filename,self.model)
        self.model_parameter_info = self.measurement_list[0].model.model_parameter_info
        return
    
    def application_initialize(self,filename):
        """Calls :func:`self.app_initialize_function` to create the application list.
        
        :param filename: The file containing the application database
        :type filename: str
        """
        self.application_list = self.app_initialize_function(filename,self.model)
        for meas in self.application_list:
            meas._status = 'Application'
        #self.model_parameter_info = self.measurement_list[0].model.model_parameter_info
        return
    
    def make_response(self):
        """Creates the response surface for each measurement. The exact behavior of this method depends on the :func:`make_response` method of the individual measurements.
        """
        for meas in self.measurement_list + self.application_list:
            meas.make_response()
        return
    
    def obj_fun(self,x):
        num_params = self.active_parameters.shape[0]
        num_expts = len(self.measurement_list)
        
        f = np.empty(num_params + num_expts)
        df = np.zeros((num_params + num_expts,num_params))
        
        inv_covar = self.solution.alpha_i
        initial_guess = self.solution.x_i

        #Set the parts of the objective function that depend on x
        f[0:num_params] = np.dot(inv_covar,(x - initial_guess))
        df[0:num_params,0:num_params] = inv_covar
        for exp_num,meas in enumerate(self.measurement_list):
            #for exp_num,resp in enumerate(response_list):
            #Evaluate 
            f_num,df_num = meas.sensitivity_response(x)
            
            f_exp = meas.value
            w = 1/meas.uncertainty
            
            f[exp_num + num_params] = (f_num - f_exp)*w
            df[exp_num + num_params,:] = df_num*w
                
        return f,df
    def run_optimization(self,initial_guess=None,initial_covariance=None):
        """Finds the constrained model and its uncertainty and creates the :py:func:`.Solution` object.
        
        :param initial_guess: The prior parameter values. If not specified, the default is the zero vector
        :param initial_covariance: The prior parameter covariance. If not specified, the default is :math:`I/4`, where I is the identity matrix
        :type inital_guess: numpy.ndarray,  len(self.active_parameters)
        :type initial_covariance: numpy.ndarray, len(self.active_parameters) x len(self.active_parameters) 
        
        
        This function finds the optimal set of model parameters based on the experimental measurements and uncertainties provided in the measurement list. It uses the Levenberg-Marquardt algorithm to solve the optimization problem:
        
        .. math::
            
            x_{\\text{opt}} = \\text{argmin}_x [\sum_i \\frac{(y_i(x) - y_{i,\\text{exp}})}{\sigma_{i,\\text{exp}}} + (x - x_{\\text{init}})^T\Sigma_{\\text{init}}^{-1}(x - x_{in\\text{init}it})]^2
        
        and it estimates the uncertainty in the optimized parameters by linearizing the objective function and calculating the covariance matrix as:
        
        .. math::
           
           \Sigma = [ \Sigma_{\\text{init}}^{-1} + \sum_i  \\frac{J_j J_j^T}{\sigma_{i,\\text{exp}}} ]^{-1}
        
        where
        
        * :math:`x` is the vector of model parameters
        * :math:`x_{\\text{init}}` is the vector of prior parameter values
        * :math:`y_{i,\\text{exp}}` is the measured value of the ith measurement
        * :math:`\sigma_{i,\\text{exp}}` is the uncertainty in the measured value of the ith measurement
        * :math:`y_i(x) = x^Tb_ix + a_i^Tx + z_i` is the response-surface-predicted value of the ith measurement
        * :math:`J_i(x) = b_ix + a_i` is the gradient of the ith response surface
        * :math:`\Sigma_{\\text{init}}` is the prior parameter covariance matrix
        
        
        """
        #def run_optimization(initial_guess,measurement_list):
        
        #Create a local pointer to the measurement list
        measurement_list = self.measurement_list
        
        from scipy import optimize as spopt
        print self.active_parameters.shape
        num_params = self.active_parameters.shape[0]#initial_guess.shape[0]
        num_expts = len(self.measurement_list)
        
        #Check to see if initial_guess and initial_covariance exist
        if initial_guess is not None:
            #Check to see if initial_guess and initial_covariance have the correct dimensions
            assert initial_guess.shape[0] == num_params
        else:
            initial_guess = np.zeros(num_params)
        if initial_covariance is not None:
            assert initial_covariance.shape[0] == num_params
            #Compute the inverse covariance matrix
            inv_covar = np.linalg.inv(initial_covariance)
        else:
            inv_covar = 4*np.eye(num_params)
        
        #f = np.zeros(num_params + num_expts)
        #df = np.zeros((num_params + num_expts,num_params))
        
        #Store the initial guess and initial inverse covariance in a Solution object
        #This will make it available to the obj_fun routine
        self.solution = Solution(initial_guess,
                                 covariance_x=inv_covar,
                                 initial_x=initial_guess,
                                 initial_covariance=inv_covar)
        
        #def obj_fun(x):
        #    #Set the parts of the objective function that depend on x
        #    f[0:num_params] = np.dot(inv_covar,(x - initial_guess))
        #    df[0:num_params,0:num_params] = inv_covar
        #    for exp_num,meas in enumerate(measurement_list):
        #        #for exp_num,resp in enumerate(response_list):
        #        #Evaluate 
        #        f_num,df_num = meas.sensitivity_response(x)
        #        
        #        f_exp = meas.value
        #        w = 1/meas.uncertainty
        #        
        #        f[exp_num + num_params] = (f_num - f_exp)*w
        #        df[exp_num + num_params,:] = df_num*w
        #        
        #    return f,df
        opt_output = spopt.root(self.obj_fun,initial_guess,method='lm',jac=True)
        #solution = spopt.root(obj_fun,initial_guess,method='lm')
        
        print opt_output.message
        
        optimal_parameters = np.array(opt_output.x)
        
        residuals,final_jac = self.obj_fun(optimal_parameters)
        
        icov = np.dot(final_jac.T,final_jac)
        cov = np.linalg.inv(icov)
        
        self.solution = Solution(optimal_parameters,
                                 covariance_x=cov,
                                 initial_x=initial_guess,
                                 initial_covariance=inv_covar)
        
        #print optimal_parameters
        return optimal_parameters,cov
    
    def validate_solution(self):
        """Calculates predicted measurement values and uncertainties based on the constrained model.
        
        Once the constrained model and associated uncertainty has been calculated, this method will evaluate the response surfaces for each measurement and calculate the corresponding uncertainty in the response-surface value based on the uncertainty in the constrained model.  The response value is found by calculating :math:`y_i(x_{opt}` and the uncertainty by calculating :math:`\sigma_{i,opt} = J_i^T\Sigma J_i` 
        
        where :math:`J_i = 2b_ix_{\\text{opt}} + a_i` is the gradient of the ith response surface
        
        In addition, the method will compare the measured values and uncertainties to the response-surface values and use this information to calculate the consistency scores, which are used in remove_inconsistent_measurements. The consistency score :math:`Z` and weighted consistency score :math:`W` are calculated as follows:
        
        * :math:`Z_i = \\frac{(y_i(x_{\\text{opt}}) - y_{i,\\text{exp}})}{2 \sigma_{i,\\text{exp}}}`
        
        * :math:`W_i = \|Z_i\| (\\frac{\sigma_{i,\\text{exp}}}{\sigma_{i,\\text{opt}}})^2`
        
        The method will then store these values as attributes of each measurement object.
        
        """
        num_expts = len(self.measurement_list)
        header_args = ('Name',
                       'Value','Unc',
                       'OptVal','OptUnc',
                       'MdlVal','MdlUnc'
                      )
        print('{:20s}  {:6s} {:6s} {:6s} {:6s} {:6s} {:6s}'.format(*header_args))
        for (exp_num,meas) in enumerate(self):
            a = meas.response.a
            b = meas.response.b
            
            #Calculate optimized values, base model uncertainties, and optimized uncertainties
            meas.optimized_value,meas.optimized_uncertainty = meas.evaluate_uncertainty(self.solution.x,self.solution.cov)
            meas.model_uncertainty = math.sqrt( np.dot(a,a.T)+2*np.trace( np.dot(b,b) ) )/2
            
            #meas.consistency =  (meas.optimized_value - meas.value) / (2 * meas.uncertainty)
            
            #uncertainty_ratio = meas.optimized_uncertainty / meas.uncertainty
            
            #meas.weighted_consistency = abs(meas.consistency) * uncertainty_ratio ** 2
            
            print_value = meas.value
            print_unc   = meas.uncertainty
            if meas.value is None:
                print_value = 0
            if meas.uncertainty is None:
                print_unc = 0
            
            print_args = (meas.name,
                          float(print_value),float(print_unc),
                          float(meas.optimized_value),float(meas.optimized_uncertainty),
                          float(meas.response.z),float(meas.model_uncertainty)
                         )
            #for arg in print_args:
            #    print arg,type(arg)                
            #    if type(arg) == type(np.array([])): print arg.shape
            #    
            print('{:20s}: {: 6.2f} {: 6.2f} {: 6.2f} {: 6.2f} {: 6.2f} {: 6.2f} '.format(*print_args))
        for (exp_num,meas) in enumerate(self.measurement_list):
            meas.consistency =  (meas.optimized_value - meas.value) / (2 * meas.uncertainty)
            uncertainty_ratio = meas.optimized_uncertainty / meas.uncertainty
            meas.weighted_consistency = abs(meas.consistency) * uncertainty_ratio ** 2
            
        return
    
    def remove_inconsistent_measurements(self):
        """Finds and removes inconsistent measurements
        
        This method will find that measurement with the largest weighted consistency and remove that measurement from the measurement list. Measurments removed in this way are added to the removed list and are still accessible.
        
        The consistency score :math:`Z` and weighted consistency score :math:`W` are calculated using :func:`validate_solution` 
        """
        optimized = False
        while optimized is False:
            z,cov = self.run_optimization()
            self.validate_solution()
            optimized = self._remove_inconsistent()
            
    def _remove_inconsistent(self):

        #Collect the consistency scores and weighted consistency scores
        zscores = np.array([meas.consistency for meas in self.measurement_list])
        wscores = np.array([meas.weighted_consistency for meas in self.measurement_list])
        
        #Sort the weighted consitency scores and then return them in descending order (starting with the biggest)
        for exp_num in np.argsort(wscores)[::-1]:
            #Check to see if the currect measurement is inconsistent. If it is, move it to the removed list and break from the loop
            if abs(zscores[exp_num]) > 1:
                meas_remove = self.measurement_list.pop(exp_num)
                meas_remove._status = 'Inconsistent'
                self.removed_list += [meas_remove]
                
                unc_ratio = meas_remove.optimized_uncertainty / meas_remove.uncertainty
                
                print_args = (meas_remove.name,unc_ratio,meas_remove.consistency,meas_remove.weighted_consistency)
                
                print("""{} 
    Uncertainty Ratio: {: 6.2f}
    Normalized Score: {: 6.2f}
    Weighted Consistency {: 6.2f}""".format(*print_args))
                
                return False
        print('No inconsistent measurements')
        return True
    
    def calculate_entropy(self):
        """Determines the rate of change of information entropy for each measurement with respect to the uncertainty in each other measurement. 
        
        This function calculates the derivative :math:`\\frac{d \ln \sigma_{i,opt}}{d \ln \sigma_{j,exp}}` for each measurement pair. The derivative is calculated using
        
        .. math::
           \\frac{d \ln \sigma_{i,\\text{opt}}}{d \ln \sigma_{j,\\text{exp}}} = \\frac{J_i^T\Sigma J_j J_j^T\Sigma J_i + 2 \\text{tr}[2b_i \\Sigma b_i \\Sigma J_j J_j^T \\Sigma] }{\sigma_{j,\\text{exp}}^2\sigma_{i,\\text{opt}}^2}
        
        where :math:`J_i = 2b_ix_{\\text{opt}} + a_i` is the gradient of the ith response surface.
        
        The entropy flux term is defined as 
        
        .. math::
           \Phi_i = \sum_j [\\frac{d \ln \sigma_{j,\\text{opt}}}{d \ln \sigma_{i,\\text{exp}}} - \\frac{d \ln \sigma_{i,\\text{opt}}}{d \ln \sigma_{j,\\text{exp}}}]
        
        """
        number_measurements = len(self.measurement_list)
        number_applications = len(self.application_list)
        number_total = len(self)
        
        entropy = np.zeros((number_total,number_total))
        
        #Outer loop of measurements
        for i,meas_i in enumerate(self.measurement_list):
            y,a_i = meas_i.sensitivity_response(self.solution.x)
            a_i = np.array([a_i]).transpose()
            aat = np.dot(a_i,a_i.T) 
            
            caatc = np.dot(self.solution.cov,np.dot(aat,self.solution.cov))
            
            for r,meas_r in enumerate(self.active):
                y,a_r = meas_r.sensitivity_response(self.solution.x)
                b_r = meas_r.response.b
                
                a_r = np.array([a_r]).transpose()
                
                artcaatcar = np.dot(a_r.T,np.dot(caatc,a_r))
                    
                b_r_times_cov  = np.dot(b_r,self.solution.cov)
                b_r_times_dcov = np.dot(b_r,caatc)
                brcbrdc = np.dot(b_r_times_cov,b_r_times_dcov)
                
                numerator = artcaatcar + 2 * np.trace(brcbrdc)
                
                entropy[i,r] = numerator / ( (meas_i.uncertainty * meas_r.optimized_uncertainty) ** 2 )
            #print 'Sensitivty of uncertainty r to experimental uncertainty ' + str(i+1)
            #print entropy[i,:]
        entropy_flux = np.diag(np.dot(entropy,entropy.T) - np.dot(entropy.T,entropy) )
        
        for entropy,meas in zip(entropy_flux,self):
            meas.entropy = entropy
            
            print_args = (meas.name,meas.entropy)
                
            print("""{} Entropy flux {: 10.6f}""".format(*print_args))

        return 
    
    def remove_low_information_measurements(self):
        """Finds and removes low-information measurements 
        
        This method will find that measurement with the largest (in absolute value) negative information entropy derivative and remove that measurement from the measurement list. Measurments removed in this way are added to the removed list and are still accessible.
        
        The consistency score :math:`\Phi` and weighted consistency score :math:`W` are calculated using :func:`validate_solution` 
        """
        minimized = False
        while minimized is False:
            self._calculate_uncertainty()
            self.validate_solution()
            self.calculate_entropy()
            minimized = self._remove_low_information()
    
    def _remove_low_information(self):
        
        entropies = np.array([meas.entropy for meas in self.measurement_list])
        
        for exp_num in np.argsort(entropies)[::-1]:
            if entropies[exp_num] < 0:
                meas_remove = self.measurement_list.pop(exp_num)
                meas_remove._status = 'Low Information'
                print_args = (meas_remove.name,meas_remove.entropy)
                
                print("""{} Entropy flux {: 6.2f}""".format(*print_args))
                return False
        print('No low-information measurements')
        return True
    
    def _calculate_uncertainty(self,initial_covariance=None,initial_guess=None):
        
        residuals,final_jac = self.obj_fun(self.solution.x)
        
        #Calculate the covariance matrix
        icov = np.dot(final_jac.T,final_jac)
        cov = np.linalg.inv(icov)
        
        #Update the covariance
        self.solution.update(new_cov=cov)
        #self.solution.cov = cov
        #self.solution.alpha = np.linalg.cholesky(cov)
        return
    
                
        
    def _single_pdf_plot(self,factors=[0,1],ax=None):
        
        if len(factors) > 2:
            raise ValueError
        
        active_params = self.active_parameters[factors]
        
        params_info = self.model_parameter_info[active_params]
        
        zred = self.solution.x[factors]
        
        alphared = self.solution.alpha[factors]\
        
        pts = np.arange(-1.5,1.5,0.01)
        xx,yy = np.meshgrid(pts,pts)
        
        XX  = np.stack((xx,yy),axis=2)
        
        S = np.dot(alphared,alphared.T)
        
        Sinv = np.linalg.inv(S)
        
        r2  = np.zeros_like(xx)
        xi2 = np.zeros_like(xx)
        
        #Get a row of the XX vector
        for rownum,row in enumerate(XX):
            #Get a single point from that row
            for colnum,point in enumerate(row):
                r2[rownum,colnum] = np.dot(point,point.T) * 4
                
                point_translate = point - zred
                xi2[rownum,colnum] = np.dot(point_translate,np.dot(Sinv,point_translate))
            
        prior_pdf = np.exp(-1*r2)
        posterior_pdf = np.exp(-1*xi2)
        
        levels = np.exp((np.arange(-2,0,0.5) ** 2) * -1)
    
        #cpr`ior = ax.contour(xx,yy,prior_pdf,levels=np.exp(np.arange(-2,0,0.5)),colors='k',linestyles='dotted')
        #cposte = ax.contour(xx,yy,posterior_pdf,levels=np.exp(np.arange(-2,0,0.5)),colors='k')
        cprior = ax.contour(xx,yy,prior_pdf,levels=levels,colors='k',linestyles='dotted')
        cposte = ax.contour(xx,yy,posterior_pdf,levels=levels,colors='k')
        
        ax.set_xlabel(params_info[0]['parameter_name'])
        ax.set_ylabel(params_info[1]['parameter_name'])
        
        ax.axis('square')
        return
    
    def plot_pdfs(self,factors_list=[0,1]):
        """Generates a plot of the joint probability density functions for several pairs of parameters.
        
        :param factors_list: A list of pairs of parameters. For each pair [x, y] the parameter x will appear on the x axis and the parameter y will appear on the y axis. If this parameter is not supplied, it defaults to [0,1].
        :type factors_list: list of length-2 lists.
        """
        
        #Get the number of plots that will be created
        num_plots = len(factors_list)
        
        #Create the matplotlib figure and subplots
        fig,axes=plt.subplots(1,num_plots,figsize=(num_plots*5,5))
        
        #Plot the individual subplots
        for ax,factors in zip(axes,factors_list):
            self._single_pdf_plot(factors=factors,ax=ax)
    
        return fig