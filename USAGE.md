
##Examples

Create a repository

    raptly create pizza/pizza4/trusty    
    
Publish / re-publish the unstable distribution 

    raptly deploy pizza/pizza4/trusty
    
Deploy a package and publish / re-publish the unstable distribution    

    raptly deploy pizza/pizza4/trusty margherita_1.0.0_all.deb
    
Show packages in the unstable distribution

    raptly show pizza/pizza4/trusty unstable
    
Create a test candidate comprising all packages from stable distribution (none yet) plus packages from unstable that 
match the query

    raptly test pizza/pizza4/trusty --packages "margherita_1.0.0_all " TKT-1234
    
Stage the test candidate in the staging distribution    
    
    raptly stage pizza/pizza4/trusty TKT-1234
    
Release the test candidate to the stable distribution

    raptly release pizza/pizza4/trusty TKT-1234
    
Show how the whole repository is constituted 

    raptly show pizza/pizza4/trusty
    
    
TODO    
Create a check distribution for development testing

    raptly check pizza/pizza4/trusty --packages "margherita"


## Command Reference

### check

The primary use case for the  `check` command is to privately check that your new changes will work with reference to 
the stable distribution.  This is illustrated below for a client with the local username `gino`.

    $ raptly check pizza/pizza4 mozzarella_1.5.3-dev_all.deb
    
    pizza/pizza4/gino pool         pizza/pizza4/gino check        pizza/pizza4  stable
    ======================         ========================       ====================
    mozzarella_1.5.3-dev_all  >>>  mozzarella_1.5.3-dev_all       mozzarella_1.5.2_all                                                                          
    [...]                          fiorentina_1.0.2_all      <<<  fiorentina_1.0.2_all                                    
                                   margherita_1.0.0_all      <<<  margherita_1.0.0_all                                
                                   meatfeast_99.1.5_all      <<<  meatfeast_99.1.5_all

In the example, Gino has developed a new version of the package `mozzarella` which is intended for the repository 
`pizza/pizza4`.  He then invokes the `raptly check` command.  A private repo is created for Gino that is derived 
from the original repo name and his local username.  Any new package(s) on the commandline are uploaded to the 
private repo's *pool*.

A new `check` distribution of the private repo is now published, comprising the uploaded packages plus the packages 
from the original repo's `stable` distribution.  

The `check` distribution is used to check that the code works in integration with all the other packages 
in the stable distribution - i.e. the current production code.  Typically, a full development stack will be created
from a given `check` distribution. 

By supplying the `--checks` argument to the `raptly show <repo name>`, you can see the official set of distributions
in addition to any check distributions you have created.

    raptly show pizza/pizza4 --checks
    
    Distributions:
      stable -> pizza_pizza4.TKT-1234.1506701691
      staging -> pizza_pizza4.TKT-1234.1506701691
      testing -> pizza_pizza4.TKT-1234.1506701691
      unstable -> pizza_pizza4.1507039393
      
    Checks:
      pizza/pizza4/gino -> 
      pizza/piiza4/mario ->
  
To manage the proliferation of `check` distributions there is only one private repo permitted per local user.  This is 
to save disk space, since every published distribution is a signed *copy* of all the binary packages in the distribution 
which occupies significant disk space.

To delete your private check repo.
    
    raptly check --clean


### deploy

The `deploy` command is used to formally 

### test    

The following example shows how a testing candidate is constructed. 

    raptly test pizza/pizza4/trusty --packages "margherita_1.1.0-beta_all|fiorentina_0.9.7_all" TKT-8904
 
    unstable                        testing                          stable
    ========                        =======                          ======
    fiorentina_0.9.7_all       >>>  fiorentina_0.9.7_all  
    fiorentina_1.0.0_all            
    fiorentina_1.0.1-beta_all       
    fiorentina_1.0.2_all            
    margherita_1.0.0_all            margherita_1.0.0_all       <<<   margherita_1.0.0_all
    margherita_1.1.0_all            
    margherita_1.1.0-2_all          
    margherita_1.1.0-beta_all  >>>  margherita_1.1.0-beta_all  
    
The stable distribution contains the single package `margherita_1.0.0_all`.  The `--packages` selection argument to the 
`test` command specifies two additional packages to be drawn into the test candidate from unstable.  This results in a 
testing candidate that contains the union of all three packages.

Note - if any of the packages specified in the `--packages` selection argument are not present in unstable, an error is 
reported.



        
    