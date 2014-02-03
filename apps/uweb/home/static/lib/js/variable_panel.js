  function deleteSelectedVariables() {
        $(".variables").each(function(index,domEle){
            if ($(domEle).prop("checked"))
            {
                elementId=$(domEle).attr('id');
                trId="tr"+elementId.substring(2);
                trElement=document.getElementById(trId);
                $(trElement).empty();
            }
        });
    }
    
    function checkAllVariables() {
        $(".variables").each(function (index,domEle) {
            if (!($(domEle).prop("checked")))
            {
                $(domEle).prop('checked',true);           
            }
        });
    }
    
    function resetVariables() {
        $(".variables").each(function(index,domEle){
            if ($(domEle).prop("checked"))
            {
                $(domEle).prop('checked',false);           
                elementId=$(domEle).attr('id');
                inputId="input"+elementId.substring(2);
                inputElement=document.getElementById(inputId);
                $(inputElement).prop('type','hidden');
                inputValue=$(inputElement).val();
                labelId="cbinp"+elementId.substring(2);
                $("#"+labelId).html(inputValue); 
            }
        });
    }

    function editSelectedVariables() {
        var ids= $('.variables:checked').map(function(){ return this.id;}).get();
        for (var i=0; i<ids.length;i++)
        {
            var new_id = "input"+ids[i].substring(2);
            my_element=document.getElementById(new_id);
            my_element.setAttribute('type','text');
            var label_id="cbinp"+ids[i].substring(2);
            $("#"+label_id).html(""); 
        }
    }
    
    