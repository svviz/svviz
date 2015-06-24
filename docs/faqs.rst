.. _faqs:

Frequently Asked Questions
==========================

.. _tunneling:

**Can I access the web interface if svviz is running on another computer (for example, a server)?**

Yes, you should be able to do this by ssh tunneling:

1. Run svviz as you normally would, but define the port using the ``--port n`` option, where ``n`` is an integer from 0-65535 corresponding to an unused port on the computer running svviz.
2. From your desktop computer, start an ssh tunnel to your server. If your server is running on myserver.com, and you used port 7777 in step 1., the following command should start the tunnel from localhost:7777 on your desktop to localhost:7777 on the server:

    .. code-block:: bash

        ssh -L 127.0.0.1:7777:127.0.0.1:7777 username@myserver.com -N

    After entering your password for myserver.com, leave ssh running in the terminal.

3. Open your browser to ``http://127.0.0.1:7777``.


