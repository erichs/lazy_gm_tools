## DMScreen

This is a responsive flexbox layout tool for organizing DM tools into an HTML display that minimizes browser tab or OS alt-tab switching during gameplay. It supports the following configuration:

visualViewport.width=1470px
visualViewport.height=735px

It's HTML content consists of 4 iFrames, all separated by a 1px solid border, each of which should be draggable to resize. Each iFrame should maximally fill the dimensions it has been sized to. The outmost HTML body should maximally fill the visualViewport dimensions.

iFrame content URLs:
top-left: docs.google.com
top-right: open.spotify.com
bottom-left: localhost:3000
bottom-right: ../../index.html
