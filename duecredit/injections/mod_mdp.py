# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

"""
Automatic injection of bibliography entries for mdp module
"""


from ..entries import Doi, BibTeX, Url

# If defined, would determine from which to which version of the corresponding
# module to care about
min_version = None
max_version = None


def inject(injector):
    injector.add('mdp', None, Doi('10.3389/neuro.11.008.2008'),
                 description="Modular toolkit for Data Processing (MDP): a Python data processing framework",
                 tags=['implementation'])

    injector.add('mdp.nodes', 'PCANode.train', Doi('10.1007/b98835'),
                 description="Principal Component Analysis (and filtering)",
                 tags=['implementation'])

    injector.add('mdp.nodes', 'NIPALSNode.train', BibTeX("""
        @incollection{Word1966,
            author={Wold, H.},
            title={Nonlinear estimation by iterative least squares procedures.},
            booktitle={Research Papers in Statistics},
            publisher={Wiley}
            year={1966},
            editor={David, F.},
            pages={411--444},
            }
        """), description="Principal Component Analysis using the NIPALS algorithm.",
        tags=['edu'])

    injector.add('mdp.nodes', 'FastICANode.train', Doi('10.1109/72.761722'),
                 description="Independent Component Analysis using the FastICA algorithm",
                 tags=['implementation'])

    injector.add('mdp.nodes', 'CuBICANode.train', Doi('10.1109/TSP.2004.826173'),
                 description='Independent Component Analysis using the CuBICA algorithm.',
                 tags=['implementation'])
    
    injector.add('mdp.nodes', 'NIPALSNode.train', BibTeX("""
        @conference{ZieheMuller1998,
            author={Ziehe, Andreas and Muller, Klaus-Robert},
            title={TDSEP an efficient algorithm for blind separation using time structure.},
            booktitle={Proc. 8th Int. Conf. Artificial Neural Networks},
            year={1998},
            editor={Niklasson, L, Boden, M, and Ziemke, T},
            publisher={ICANN}
            }
        """), description='Independent Component Analysis using the TDSEP algorithm',
        tags=['edu'])


    injector.add('mdp.nodes', 'JADENode.train', Doi('10.1049/ip-f-2.1993.0054'),
                    description='Independent Component Analysis using the JADE algorithm',
                    tags=['implementation'])
    injector.add('mdp.nodes', 'JADENode.train', Doi('10.1162/089976699300016863'),
                    description='Independent Component Analysis using the JADE algorithm',
                    tags=['implementation'])

    injector.add('mdp.nodes', 'SFANode.train', Doi('10.1162/089976602317318938'),
                    description='Slow Feature Analysis',
                    tags=['implementation'])

    injector.add('mdp.nodes', 'SFA2Node.train', Doi('10.1162/089976602317318938'),
                    description='Slow Feature Analysis (via the space of inhomogeneous polynomials)',
                    tags=['implementation'])
    

    injector.add('mdp.nodes', 'ISFANode.train', Doi('10.1007/978-3-540-30110-3_94'),
                    description='Independent Slow Feature Analysis',
                    tags=['implementation'])

 
    injector.add('mdp.nodes', 'XSFANode.train', BibTeX("""
        @article{SprekelerZitoWiskott2009,
            author={Sprekeler, H., Zito, T., and Wiskott, L.},
            title={An Extension of Slow Feature Analysis for Nonlinear Blind Source Separation.},
            journal={Journal of Machine Learning Research.},
            year={2009},
            volume={15},
            pages={921--947},
            }
        """), description="Non-linear Blind Source Separation using Slow Feature Analysis",
        tags=['edu'])

    injector.add('mdp.nodes', 'FDANode.train', BibTeX("""
        @book{Bishop2011,
            author={Bishop, Christopher M.},
            title={Neural Networks for Pattern Recognition},
            publisher={Oxford University Press, Inc}
            year={2011},
            pages={105--112},
            }
        """), description="(generalized) Fisher Discriminant Analysis",
        tags=['edu'])

    # etc...
