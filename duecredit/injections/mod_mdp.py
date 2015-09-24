#!/usr/bin/python

"""
#----------------------------------------------------------------
Author: Jason Gors <jasonDOTgorsATgmail>
Creation Date: 09-22-2015
Purpose:  Automatic injection of bibliography entries for mdp module
#----------------------------------------------------------------
"""


from ..entries import Doi, BibTeX, Url

# If defined, would determine from which to which version of the corresponding
# module to care about
min_version = None
max_version = None

'''
injector.add('', None, Doi(''),
                description="",
                tags=['implementation'])
'''

def inject(injector):
    injector.add('mdp', None, Doi('10.3389/neuro.11.008.2008'),
                 description="Modular toolkit for Data Processing (MDP): a Python data processing frame work.",
                 tags=['implementation'])

    injector.add('mdp.nodes', 'PCANode', Doi('10.1007/b98835'),
                 description="Filter the input data through the most significatives of its principal components.",
                 tags=['implementation'])

    injector.add('mdp.nodes', 'NIPALSNode', BibTeX("""
        @incollection{Word1966,
            author={Wold, H.},
            title={Nonlinear estimation by iterative least squares procedures.},
            booktitle={Research Papers in Statistics},
            publisher={Wiley}
            year={1966},
            editor={David, F.},
            pages={411-444},
            }
        """), description="Perform Principal Component Analysis using the NIPALS algorithm.", 
        tags=['edu'])

    injector.add('mdp.nodes', 'FastICANode', Doi('10.1109/72.761722'),
                 description="Perform Independent Component Analysis using the FastICA algorithm",
                 tags=['implementation'])

    injector.add('mdp.nodes', 'CuBICANode', Doi('10.1109/TSP.2004.826173'),
                 description='Perform Independent Component Analysis using the CuBICA algorithm.',
                 tags=['implementation'])
    
    injector.add('mdp.nodes', 'NIPALSNode', BibTeX("""
        @conference{ZieheMuller1998,
            author={Ziehe, Andreas and Muller, Klaus-Robert},
            title={TDSEP an efficient algorithm for blind separation using time structure.},
            booktitle={Proc. 8th Int. Conf. Artificial Neural Networks},
            year={1998},
            editor={Niklasson, L, Boden, M, and Ziemke, T},
            publisher={ICANN}
            }
        """), description="Perform Independent Component Analysis using the TDSEP algorithm.", 
        tags=['edu'])


    injector.add('mdp.nodes', 'JADENode', Doi('10.1049/ip-f-2.1993.0054'),
                    description='Perform Independent Component Analysis using the JADE algorithm.',
                    tags=['implementation'])
    injector.add('mdp.nodes', 'JADENode', Doi('10.1162/089976699300016863'),
                    description='Perform Independent Component Analysis using the JADE algorithm.',
                    tags=['implementation'])

    injector.add('mdp.nodes', 'SFANode', Doi('10.1162/089976602317318938'),
                    description='Extract the slowly varying components from the input data.',
                    tags=['implementation'])

    injector.add('mdp.nodes', 'SFA2Node', Doi('10.1162/089976602317318938'),
                    description='Get an input signal, expand it in the space of inhomogeneous polynomials of degree 2 and extract its slowly varying components.',
                    tags=['implementation'])
    

    injector.add('mdp.nodes', 'ISFANode', Doi('10.1007/978-3-540-30110-3_94'),
                    description='Perform Independent Slow Feature Analysis on the input data.',
                    tags=['implementation'])

 
    injector.add('mdp.nodes', 'XSFANode', BibTeX("""
        @article{SprekelerZitoWiskott2009,
            author={Sprekeler, H., Zito, T., and Wiskott, L.},
            title={An Extension of Slow Feature Analysis for Nonlinear Blind Source Separation.},
            journal={Journal of Machine Learning Research.},
            year={2009},
            volume={15},
            pages={921-947},
            }
        """), description="Perform Non-linear Blind Source Separation using Slow Feature Analysis.", 
        tags=['edu'])

    injector.add('mdp.nodes', 'FDANode._train', BibTeX("""
        @book{Nishop2011,
            author={Christopher M. Bishop},
            title={Neural Networks for Pattern Recognition},
            publisher={Oxford University Press, Inc}
            year={2011},
            pages={105-112},
            }
        """), description="Perform a (generalized) Fisher Discriminant Analysis of its input.", 
        tags=['edu'])

    # etc...
