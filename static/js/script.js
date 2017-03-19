google.load('visualization', '1.0', {'packages':['corechart']});
google.load("visualization", "1.1", {packages:["bar"]});
// google.load("visualization", "1.1", {packages:["table"]});
google.load('visualization', '1.0', {'packages':['table']});
$(document).ready(function() {
  setTimeout(api_call3(), 4000);
});
    function api_call(){
           $.ajax({
              type: 'GET',
              url: 'http://localhost:5000/todo/api/v1.0/search_by_phone/' + $("#text_bar").val(),
              success: get_data
            });   // Ajax Call
    };

    function get_data(data){
        console.log(data);
        input = JSON.parse(data);
        var data = google.visualization.arrayToDataTable([
         ['Element', '%', { role: 'style' }],
         ['Price', input.price, '#F2671F'],            // RGB value
         ['Product', input.product, '#C91B26'],            // English color name
         ['Delivery', input.delivery, '#9C0F5F'],
         ['Seller', input.seller, 'color: #60047A' ], // CSS-style declaration
         ['Warranty', input.warranty, '#160A47'],
      ]);
          
          // Set chart options
          var options = {'title':input.title,
                         'width':500,
                         'height':350,
                         animation: {"startup": true, duration:1000, easing:'out'},
                         
                         };

          // Instantiate and draw our chart, passing in some options.
          var chart = new google.visualization.BarChart(document.getElementById('chart_div'));
          chart.draw(data, options);

          function selectHandler() {
            var selectedItem = chart.getSelection()[0];
            if (selectedItem) {
              var value = data.getValue(selectedItem.row, 0);
              // alert('The user selected ' + value);
            }
          }

        // Listen for the 'select' event, and call my function selectHandler() when
        // the user selects something on the chart.
        google.visualization.events.addListener(chart, 'select', selectHandler);

        $('#bottom_right').html('');
      $('#bottom_left').html('');




          var data2 = google.visualization.arrayToDataTable([
         ['Element', 'Count', { role: 'style' }],
         ['Battery', input.attributes.battery, '#FFA200'],            // RGB value
         ['Build', input.attributes.build, '#00A03E'],            // English color name
         ['Camera', input.attributes.camera, '#24A8AC'],
         ['Display', input.attributes.display, 'color: #0087CB' ], // CSS-style declaration
         ['Sound', input.attributes.sound, '#982395'],
         ['Specs', input.attributes.specs, '#260126'],
      ]);

          var chart2 = new google.visualization.BarChart(document.getElementById('another_pie'));

          var options2 = {'title':'Product Attributes Distribution',
                          animation: {"startup": true, duration:1500, easing:'out'},
                         'width':500,
                         'height':350};

          function selectHandler2() {
            var selectedItem = chart.getSelection()[0];
            if (selectedItem) {
              var value = data2.getValue(selectedItem.row, 0);
              // alert('The user selected ' + value);
            }
          }

          $('#bottom_right').html('');
      $('#bottom_left').html('');

          google.visualization.events.addListener(chart2, 'select', selectHandler2);

          chart2.draw(data2, options2);

          
    

  };

function api_call2(){
           $.ajax({
              type: 'GET',
              url: 'http://localhost:5000/todo/api/v1.0/sentiment/' + $("#text_bar").val(),
              success: getdata2
            });   // Ajax Call
    };

function getdata2(data2) {
      // console.log(data2);
      input = JSON.parse(data2);
      var data = google.visualization.arrayToDataTable([
        ['Attribute', 'Positive', 'Negative'],
        ['Price', input.price.pos, input.price.neg],
        ['Product', input.product.whole.pos, input.product.whole.neg],
        ['Delivery', input.delivery.pos, input.delivery.neg],
        ['Seller', input.seller.neg, input.seller.neg],
        ['Warranty', input.warranty.pos, input.warranty.neg]
      ]);

      var options = {
        title: "Sentiment of " + input.title + "'s attributes",
        chartArea: {width: '50%'},
        animation: {"startup": true, duration:1000, easing:'out'},
        hAxis: {
          title: 'Number of reviews',
          minValue: 0,
          textStyle: {
            bold: true,
            fontSize: 12,
            color: '#4d4d4d'
          },
          titleTextStyle: {
            bold: true,
            fontSize: 18,
            color: '#4d4d4d'
          }
        },
        vAxis: {
          title: 'Attributes',
          textStyle: {
            fontSize: 14,
            bold: true,
            color: '#848484'
          },
          titleTextStyle: {
            fontSize: 14,
            bold: true,
            color: '#848484'
          }
        }
      };

      $('#bottom_right').html('');
      $('#bottom_left').html('');

      var chart = new google.visualization.BarChart(document.getElementById('chart_div'));
      chart.draw(data, options);

      function selectHandler() {
          var selectedItem = chart.getSelection()[0];
          if (selectedItem) {
            var category = data.getValue(selectedItem.row, 0);
            var sentiment = data.getColumnLabel(selectedItem.column);
            var table_title = category + ' Reviews';
            category = String(category.toLowerCase()); 
            // console.log(input);

            if (category=='product'){
              var reviews = input['product']['whole'];
            }
            else {
              var reviews = input[category];
            }
            if (sentiment=='Positive'){
                // console.log(reviews['pos_rev']);
                console.log(reviews);
                var data_review = new google.visualization.DataTable();
                data_review.addColumn('string', table_title);
                console.log('category positive mein hoon');
                for (i=0; i<reviews['pos_rev'].length ; i++){
                  data_review.addRow([reviews['pos_rev'][i]]);
                }

                var table = new google.visualization.Table(document.getElementById('bottom_left'));

                

              table.draw(data_review, {showRowNumber: true, width: '100%', height: '100%'});
                // alert(reviews['pos_rev']);
            };
            if (sentiment=='Negative'){
              var data_review = new google.visualization.DataTable();
                data_review.addColumn('string', table_title);
                console.log('category negative mein hoon');
                for (i=0; i<reviews['pos_rev'].length ; i++){
                  data_review.addRow([reviews['neg_rev'][i]]);
                }

                var table = new google.visualization.Table(document.getElementById('bottom_left'));

              table.draw(data_review, {showRowNumber: true, width: '100%', height: '100%'});
                // console.log(reviews['pos_rev']);
                // alert(reviews['neg_rev']);  
            };
                       
          }
          }

        // Listen for the 'select' event, and call my function selectHandler() when
        // the user selects something on the chart.
        google.visualization.events.addListener(chart, 'select', selectHandler);


      var data2 = google.visualization.arrayToDataTable([
        ['Attribute', 'Positive', 'Negative'],
        ['Battery', input.product.battery.pos, input.product.battery.neg],
        ['Build', input.product.build.pos, input.product.build.neg],
        ['Camera', input.product.camera.pos, input.product.camera.neg],
        ['Display', input.product.display.neg, input.product.display.neg],
        ['Sound', input.product.sound.pos, input.product.sound.neg],
        ['Specs', input.product.specs.pos, input.product.specs.neg]
      ]);

      var options2 = {
        title: "Sentiment of " + input.title + "'s product attributes",
        chartArea: {width: '50%'},
        animation: {"startup": true, duration:1500, easing:'out'},
        hAxis: {
          title: 'Number of reviews',
          minValue: 0,
          textStyle: {
            bold: true,
            fontSize: 12,
            color: '#4d4d4d'
          },
          titleTextStyle: {
            bold: true,
            fontSize: 18,
            color: '#4d4d4d'
          }
        },
        vAxis: {
          title: 'Attributes',
          textStyle: {
            fontSize: 14,
            bold: true,
            color: '#848484'
          },
          titleTextStyle: {
            fontSize: 14,
            bold: true,
            color: '#848484'
          }
        }
      };
      var chart2 = new google.visualization.BarChart(document.getElementById('another_pie'));
      chart2.draw(data2, options2);

      function selectHandler2() {
          console.log('selectHandler2 is called');
          var selectedItem = chart2.getSelection()[0];
          if (selectedItem) {
            var category = data2.getValue(selectedItem.row, 0);
            var sentiment = data2.getColumnLabel(selectedItem.column);
            var table_title = category + ' Reviews';
            category = String(category.toLowerCase());
            var reviews = input['product'][category];
            
            if (sentiment=='Positive'){
                var data_review = new google.visualization.DataTable();
                data_review.addColumn('string', table_title);
                console.log('Length of reviews is ' + reviews['pos_rev']);
                for (i=0; i<reviews['pos_rev'].length ; i++){
                  data_review.addRow([reviews['pos_rev'][i]]);
                }

                var table = new google.visualization.Table(document.getElementById('bottom_right'));

              table.draw(data_review, {showRowNumber: true, width: '100%', height: '100%',
                                       page:'enabled', pageSize:5});
               
            };
            if (sentiment=='Negative'){
              var data_review = new google.visualization.DataTable();

                data_review.addColumn('string', table_title);
                console.log('Length of reviews is ' + reviews['neg_rev']);
                for (i=0; i<reviews['neg_rev'].length ; i++){
                  data_review.addRow([reviews['neg_rev'][i]]);
                }

                var table = new google.visualization.Table(document.getElementById('bottom_right'));

              table.draw(data_review, {showRowNumber: true, width: '100%', height: '100%'});
            };
                       
          }
          }
         google.visualization.events.addListener(chart2, 'select', selectHandler2);

    }

function api_call3(){

           $.ajax({
              type: 'GET',
              url: 'http://localhost:5000/todo/api/v1.0/overall',
              success: getdata3
            });   // Ajax Call
    };

function getdata3(data3) {
      console.log('hhusfas');
      input = JSON.parse(data3);
      var data = google.visualization.arrayToDataTable([
        ['Attribute', 'Positive', 'Negative'],
        ['Price', input.price.pos, input.price.neg],
        ['Product', input.product.whole.pos, input.product.whole.neg],
        ['Delivery', input.delivery.pos, input.delivery.neg],
        ['Seller', input.seller.neg, input.seller.neg],
        ['Warranty', input.warranty.pos, input.warranty.neg]
      ]);

      var options = {
        title: "Sentiment of all mobile phones on Amazon and Flipkart",
        chartArea: {width: '50%'},
        animation: {"startup": true, duration:1000, easing:'out'},
        hAxis: {
          title: 'Number of reviews',
          minValue: 0,
          textStyle: {
            bold: true,
            fontSize: 12,
            color: '#4d4d4d'
          },
          titleTextStyle: {
            bold: true,
            fontSize: 18,
            color: '#4d4d4d'
          }
        },
        vAxis: {
          title: 'Attributes',
          textStyle: {
            fontSize: 14,
            bold: true,
            color: '#848484'
          },
          titleTextStyle: {
            fontSize: 14,
            bold: true,
            color: '#848484'
          }
        }
      };
      var chart = new google.visualization.BarChart(document.getElementById('chart_div'));
      chart.draw(data, options);
      $('#bottom_right').html('');
      $('#bottom_left').html('');

      $('#text_bar').val(''); //Resetting the search bar to empty string

      function selectHandler() {
          var selectedItem = chart.getSelection()[0];
          if (selectedItem) {
            var category = data.getValue(selectedItem.row, 0);
            var sentiment = data.getColumnLabel(selectedItem.column);
            var table_title = category + ' Contributors';
            category = String(category.toLowerCase()); 
            console.log(input);

            if (category=='product'){
              var reviews = input['product']['whole'];
            }
            else {
              var reviews = input[category];
            }
            if (sentiment=='Positive'){
                // console.log(reviews['pos_rev']);
                console.log(reviews);
                var data_review = new google.visualization.DataTable();
                data_review.addColumn('string', table_title);
                console.log('category positive mein hoon');
                console.log(reviews['pos_contribute'].length);
                for (i=0; i<reviews['pos_contribute'].length ; i++){
                  data_review.addRow([reviews['pos_contribute'][i][0]]);
                }

                var table = new google.visualization.Table(document.getElementById('bottom_left'));

                function countHandler() {
                var selectedItem = table.getSelection()[0];
                if (selectedItem) {
                  var topping = data_review.getValue(selectedItem.row,0);
                  // alert('The user selected ' + topping);
                  $('#text_bar').val(topping);
                  $.ajax({
                    type: 'GET',
                    url: 'http://localhost:5000/todo/api/v1.0/sentiment/' + topping,
                    success: getdata2
                      });  
                  }
              };

        google.visualization.events.addListener(table, 'select', countHandler);

              table.draw(data_review, {showRowNumber: true, width: '100%', height: '100%'});
                // alert(reviews['pos_rev']);
            };
            if (sentiment=='Negative'){
              var data_review = new google.visualization.DataTable();
                data_review.addColumn('string', table_title);
                console.log('category negative mein hoon');
                for (i=0; i<reviews['neg_contribute'].length ; i++){
                  data_review.addRow([reviews['neg_contribute'][i][0]]);
                }



                var table = new google.visualization.Table(document.getElementById('bottom_left'));

                function countHandler2() {
                var selectedItem = table.getSelection()[0];
                if (selectedItem) {
                  var topping = data_review.getValue(selectedItem.row,0);
                  // alert('The user selected ' + topping);
                  $('#text_bar').val(topping);
                  $.ajax({
                    type: 'GET',
                    url: 'http://localhost:5000/todo/api/v1.0/sentiment/' + topping,
                    success: getdata2
                      });  
                  }
              };

        google.visualization.events.addListener(table, 'select', countHandler2);



              table.draw(data_review, {showRowNumber: true, width: '100%', height: '100%'});


                // console.log(reviews['pos_rev']);
                // alert(reviews['neg_rev']);  
            };
                       
          }
          }

        // Listen for the 'select' event, and call my function selectHandler() when
        // the user selects something on the chart.
        google.visualization.events.addListener(chart, 'select', selectHandler);

      var data2 = google.visualization.arrayToDataTable([
        ['Attribute', 'Positive', 'Negative'],
        ['Battery', input.product.battery.pos, input.product.battery.neg],
        ['Build', input.product.build.pos, input.product.build.neg],
        ['Camera', input.product.camera.pos, input.product.camera.neg],
        ['Display', input.product.display.neg, input.product.display.neg],
        ['Sound', input.product.sound.pos, input.product.sound.neg],
        ['Specs', input.product.specs.pos, input.product.specs.neg]
      ]);

      var options2 = {
        title: "Sentiment of product attributes",
        chartArea: {width: '50%'},
        animation: {"startup": true, duration:1500, easing:'out'},
        hAxis: {
          title: 'Number of reviews',
          minValue: 0,
          textStyle: {
            bold: true,
            fontSize: 12,
            color: '#4d4d4d'
          },
          titleTextStyle: {
            bold: true,
            fontSize: 18,
            color: '#4d4d4d'
          }
        },
        vAxis: {
          title: 'Attributes',
          textStyle: {
            fontSize: 14,
            bold: true,
            color: '#848484'
          },
          titleTextStyle: {
            fontSize: 14,
            bold: true,
            color: '#848484'
          }
        }
      };
      var chart2 = new google.visualization.BarChart(document.getElementById('another_pie'));
      chart2.draw(data2, options2);

      function selectHandler2() {
          console.log('selectHandler2 is called');
          var selectedItem = chart2.getSelection()[0];
          if (selectedItem) {
            var category = data2.getValue(selectedItem.row, 0);
            var sentiment = data2.getColumnLabel(selectedItem.column);
            var table_title = category + ' Contributors';
            category = String(category.toLowerCase());
            var reviews = input['product'][category];
            
            if (sentiment=='Positive'){
                var data_review = new google.visualization.DataTable();
                data_review.addColumn('string', table_title);
                console.log('Length of reviews is ' + reviews['pos_contribute'].length);
                for (i=0; i<reviews['pos_contribute'].length ; i++){
                  console.log(i + "   " + reviews['pos_contribute'][i][0]);
                  data_review.addRow([reviews['pos_contribute'][i][0]]);
                }

                var table = new google.visualization.Table(document.getElementById('bottom_right'));

                function countHandler() {
                var selectedItem = table.getSelection()[0];
                if (selectedItem) {
                  var topping = data_review.getValue(selectedItem.row,0);
                  // alert('The user selected ' + topping);
                  $('#text_bar').val(topping);
                  $.ajax({
                    type: 'GET',
                    url: 'http://localhost:5000/todo/api/v1.0/sentiment/' + topping,
                    success: getdata2
                      });  
                  }
              };

        google.visualization.events.addListener(table, 'select', countHandler);

              table.draw(data_review, {showRowNumber: true, width: '100%', height: '100%'
                                       });
               
            };
            if (sentiment=='Negative'){
              var data_review = new google.visualization.DataTable();

                data_review.addColumn('string', table_title);
                console.log('Length of reviews is ' + reviews['neg_contribute'].length);
                for (i=0; i<reviews['neg_contribute'].length ; i++){
                  data_review.addRow([reviews['neg_contribute'][i][0]]);
                }

                var table = new google.visualization.Table(document.getElementById('bottom_right'));

              function countHandler2() {
                var selectedItem = table.getSelection()[0];
                if (selectedItem) {
                  var topping = data_review.getValue(selectedItem.row,0);
                  // alert('The user selected ' + topping);
                  $('#text_bar').val(topping);
                  $.ajax({
                    type: 'GET',
                    url: 'http://localhost:5000/todo/api/v1.0/sentiment/' + topping,
                    success: getdata2
                      });  
                  }
              };             

        google.visualization.events.addListener(table, 'select', countHandler2);

              table.draw(data_review, {showRowNumber: true, width: '100%', height: '100%'});
            };
                       
          }
          }
         google.visualization.events.addListener(chart2, 'select', selectHandler2);
    }








