var current_user=0;
function whoami(){
    $.ajax({
        url:'/current',
        type:'GET',
        contentType: 'application/json',
        dataType:'json',
        success: function(response){
            //alert(JSON.stringify(response));
            $('#cu_username').html(response['username']);
            current_user=response['id'];
            var name = response['name']+" "+response['fullname'];
            $('#cu_name').html(name);
        },
        error: function(response){
            //alert(JSON.stringify(response));
        }
    });
}

function allusers(){
    $.ajax({
        url:'/users',
        type:'GET',
        contentType: 'application/json',
        dataType:'json',
        success: function(response){
            //alert(JSON.stringify(response));
            var i = 0;
            $.each(response, function(){
                if(current_user!=response[i].id){
                    f = '<div class="btn btn-light btn-lg btn-block" onclick="showmessages('+response[i].id+')">';
                    f = f + response[i]['username'];
                    f = f + '</div>';
                    $('#allusers').append(f);
                }
                i = i+1;
            });
        },
        error: function(response){
            alert(JSON.stringify(response));
        }
    });
}

function wait(ms){
   var start = new Date().getTime();
   var end = start;
   while(end < start + ms) {
     end = new Date().getTime();
  }
}

function showmessages(to_id){
    $('#Enviar').empty();
    $('#Enviar').append('<input type="button" class="btn btn-success-secondary" value="Send" onclick="newMessage('+current_user+','+to_id+')"/>');
    allmessages2(current_user,to_id);
}

function allmessages2(id_from,id_to){
    $('#allmessages').empty();
    currentClickedId = id_to;
    $.ajax({
        url:'/messages/'+id_from+"/"+id_to,
        type:'GET',
        contentType: 'application/json',
        dataType:'json',
        success: function(response){
           var size_mes = response[0].length+response[1].length;
           var a_b=0;
           var b_a=0;
           for(var i=0;i<size_mes;i++){
                if(response[0].length>0 && response[1].length>0){
                    if(response[0][a_b].id<response[1][b_a].id){
                        f = '<div class="btn btn-success" style="float: right" >';
                        f = f + response[0][a_b]['content'];
                        f = f + '</div>'+'<br/><br/>';
                        $('#allmessages').prepend(f);
                        a_b=a_b+1;
                    }else{
                        f = '<div class="btn btn-warning" style="float: left" >';
                        f = f + response[1][b_a]['content'];
                        f = f + '</div>'+'<br/><br/>';
                        $('#allmessages').prepend(f);
                        b_a=b_a+1;
                    }
                }else{
                    if(response[0].length>0){
                        f = '<div class="btn btn-success" style="float: right" >';
                        f = f + response[0][i]['content'];
                        f = f + '</div>'+'<br/><br/>';
                        $('#allmessages').prepend(f);
                    }
                    if(response[1].length>0){
                        f = '<div class="btn btn-warning" style="float: left" >';
                        f = f + response[1][i]['content'];
                        f = f + '</div>'+'<br/><br/>';
                        $('#allmessages').prepend(f);
                    }
                }
           }
        },
        error: function(response){
            alert(JSON.stringify(response));
        }
    });
}

function allmessages(id_from,id_to){
    $('#allmessages').empty();
    $.ajax({
        url:'/messages',
        type:'GET',
        contentType: 'application/json',
        dataType:'json',
        success: function(response){
            //alert(JSON.stringify(response));
            var i = 0;
            $.each(response, function(){
                //alert(response[i]['user_from_id']+' '+response[i]['user_to_id']);
                if(response[i]['user_from_id']==id_from && response[i]['user_to_id']==id_to){
                    f = '<div class="btn btn-success" style="float: right" >';
                    f = f + response[i]['content'];
                    f = f + '</div>'+'<br/><br/>';
                    $('#allmessages').append(f);
                }
                if(response[i]['user_from_id']==id_to && response[i]['user_to_id']==id_from){
                    f = '<div class="btn btn-warning" style="float: left" >';
                    f = f + response[i]['content'];
                    f = f + '</div>'+'<br/><br/>';
                    $('#allmessages').append(f);
                }
                i = i+1;
            });
        },
        error: function(response){
            alert(JSON.stringify(response));
        }
    });
}

function newMessage(from_id,to_id){
    var user_to_id = to_id;
    var content = $('#content').val();
    var user_from_id = from_id;
    var message = JSON.stringify({
        "user_from_id": user_from_id,
        "user_to_id": user_to_id,
        "content": content
    });
    $.ajax({
        url:'/messages',
        type:'POST',
        contentType: 'application/json',
        data : message,
        dataType:'json',
        success: function(response){
        },
        error: function(response){
            if(response['status']==401){
                alert('No se puedo enviar el mensaje');
            }else{
                $('#confirmacion').html('Mensaje enviado');
            }
        }
    });
    showmessages(to_id);
}

function logout(){
    $.ajax({
        url:'/logout',
        type:'GET',
        success: function(response){
            location.href=response
        }
    });
}