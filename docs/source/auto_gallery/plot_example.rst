.. note::
    :class: sphx-glr-download-link-note

    Click :ref:`here <sphx_glr_download_auto_gallery_plot_example.py>` to download the full example code
.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_gallery_plot_example.py:


This is my example script
=========================

Docstring for this example



.. image:: /auto_gallery/images/sphx_glr_plot_example_001.png
    :class: sphx-glr-single-img





.. code-block:: default


    import numpy as np
    import matplotlib.pyplot as plt

    np.random.seed(1)

    alt = np.linspace(77e3, 120e3, num=200)
    dat = np.random.randn(200)

    plt.plot(alt, dat)
    plt.show()

.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  0.132 seconds)


.. _sphx_glr_download_auto_gallery_plot_example.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download

     :download:`Download Python source code: plot_example.py <plot_example.py>`



  .. container:: sphx-glr-download

     :download:`Download Jupyter notebook: plot_example.ipynb <plot_example.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_
