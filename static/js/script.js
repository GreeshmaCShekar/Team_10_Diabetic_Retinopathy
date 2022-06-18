    var img1 = document.getElementById('image1');
     var img2 = document.getElementById('image2');
      var img3 = document.getElementById('image3');
       var img4 = document.getElementById('image4');
       var h1 = document.getElementById('first_h2');
        var h2 = document.getElementById('second_h2');

       function show(){
       img1.style.display='none';
       img2.style.display='none';
       img3.style.display='block';
       img4.style.display='block';
       h1.style.display='none';
       h2.style.display='block';

       }
        function show1(){
       img1.style.display='inline';
       img2.style.display='inline';
       img3.style.display='none';
       img4.style.display='none';
         h1.style.display='block';
         h2.style.display='none';
       }