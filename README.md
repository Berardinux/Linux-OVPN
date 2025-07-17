<h2>Welcome to a LinuxOVPN!</h1>
<img src="image/LinuxOVPN-0.png" alt="Alt text" width="300"/>

<h4>
  Howdy, Berardinux here!!
  <br><br>
  &nbsp; &nbsp; LinuxOVPN is my version of the OpenVPN Connect application available on MacOS and Windows. In its current state, you will be able to import “.ovpn” files, edit the profiles once imported, and connect to them through the GUI. You can import and connect to password-protected profiles, and the application encrypts the passwords you enter before storing them. The encryption key for unencrypting your passwords is generated only after you install LinuxOVPN and is stored locally on your system. 
  <br><br>
  &nbsp; &nbsp; I will continue to work on the application, but my time is limited. I work a full-time job and attend school as well, so progress will be slow. Please share any bugs or problems you find with the application, but it may take me a while to address the issue. If you want to take it into your own hands to improve the application, you are more than welcome to take the code and fork it and try to create an improved version of what I have created so far.
  <br><br>
  &nbsp; &nbsp; Just to inform the users of the application, I am not a professional developer; I just love tinkering with technology. With that being said, I am sure that there are problems with the application, and it was the first time I have implemented encryption into one of my applications, so if there are problems, let me know. I did the best I could with my current abilities and knowledge.
  <br><br>
  &nbsp; &nbsp; The reason I created this application is that I believe the Linux operating system is amazing, and I would like to give back to the open-source community that has inspired my love for technology.
  <br><br>
  Thanks, Berardinux!
</h4>
<br>
<h3>Installation:</h3>
<h4>Run this in the directory where you would like to download the files for the application.</h4>
<pre><code>git clone https://github.com/Berardinux/Linux-OVPN.git</code></pre>
<h4>To install the application, go into the download directory and run this next command.</h4>
<pre><code>sudo ./install.sh</code></pre>
<h4>
  Go through the two menus asking whether you would like to install openvpn and LinuxOVPN, type “Y” or just hit enter on both and it will install the application and its dependencies. Once installed, you can hit your meta key on your keyboard and type LinuxOVPN and it should pop up and you should be able to run it from there. 
</h4>
<br>
<h3>Uninstall:</h3>
<h4>Run this to uninstall LinuxOVPN.</h4>
<pre><code>sudo /opt/LinuxOVPN/scripts/uninstall.sh</code></pre>
<h4>You can also uninstall LinuxOVPN through the application at the bottom of the settings window.</h4>
