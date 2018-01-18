# raptly ![build](https://travis-ci.org/arthurcrawford/test1.svg?branch=master)

Raptly is a release workflow tool and remote client for [aptly](https://www.aptly.info/), the Debian 
repository manager.

It is written in Python and is available for macOS (Homebrew) and Linux (Debian).

### Installation

#### macOS (Homebrew) 

    $ brew tap a4pizza/oven
    $ brew install raptly

#### Linux (Debian)

    $ wget https://github.com/a4pizza/test1/releases/download/${version}/raptly_${version}_all.deb
    $ dpkg -i raptly_${version}_all.deb

### Configuration

Create a configuration file containing the URL of your `aptly` server API and include any required 
authentication credentials (the two supported auth methods are: basic auth, and SSL client cert/key pair).

    $ cat ~/.raptly/config
    [default]
    url = "https://myrepo.example.com/api"
    # Client cert authentication
    cert = "~/.raptly/client.crt"
    key = "~/.raptly/client.key"
    
### Check the installation
    
```
$ raptly
usage: raptly [--url URL] [-h] [--version] [-v] [-k] [--key KEY] [--cert CERT]
              [-u USER]
              <command> ...
...

$ raptly version
raptly version: x.x.x
server version: x.x.x
```

### Rationale

`raptly` was originally devised to ease some of the common tasks encountered when using the `aptly` as part of a 
software delivery lifecycle (SDLC).

The diagram illustrates the simple SDLC workflow `raptly` is designed to support.  

```
package
   +
   +--> check ≡ δ(stable)
   |
   |    +==========+                                +========+
   +--> | unstable | +--> testing +--> staging +--> | stable |
        +==========+                                +========+
        
             <- - - - - - release pipeline - - - - - - ->    
```    
*[A *repository (repo)* is a database of uploaded packages stored on the `aptly` server.
 A *distribution* is a published set of packages from a repo which can be used as an APT source.  ]*
 
As a new package version moves through each stage of the SDLC, it is published in the accompanying distribution. 


A *check* distribution may be created during development to check that all unit and system integration tests are 
satisfied for a given package prior to its deployment into the release pipeline.  A check distribution is a derivative 
of the current stable distribution - i.e. it is the same list of packages but with the addition of the new package 
version under test.

The *unstable* distribution, the beginning of the release pipeline, receives checked packages.  

Each newly checked package version in unstable is ready for testing; it may be incorporated into a testing distribution 
for QA.  

Following successful testing, the test distribution may be promoted into staging, for operational validation.

Finally the candidate distribution may be promoted to *stable*, where the new package version becomes available 
for updating the production systems.

### Usage

##### Show all repos

    $ raptly show 
    
##### Create a new repo

    $ raptly create a4pizza/base

##### Show a specific repo

    $ raptly show a4pizza/base
    
##### Show a specific published distribution
    
    $ raptly show a4pizza/base unstable    

#### Deploy a package

    $ raptly deploy a4pizza/base fiorentina_0.9.7_all.deb
  
##### Test a package

    $ raptly test a4pizza/base -p fiorentina_0.9.7_all TKT-123

##### Stage a package

    $ raptly stage a4pizza/base TKT-123
    
##### Release a package

    $ raptly release a4pizza/base TKT-123
    
##### Check a package

    $ raptly check a4pizza/base fiorentina_1.0.0_all.deb

    

    
    
    
    
