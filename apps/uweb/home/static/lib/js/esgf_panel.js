$('#esgf_result').on('click','a.esgf_file_toggle',function(){
    ul_node=$(this).parent().next().find('.esgf_file_ul');
    alert(ul_node);
});
