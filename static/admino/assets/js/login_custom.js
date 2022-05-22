/*proloader*/
function load()
{
  document.querySelector('.placeholder').style.display="none";
  document.querySelector('.main-display').style.display="block";
}

/*insection observer API */
function observerImages()
{
    var images=document.querySelectorAll('[data-src]'),
    imgOpts={},
    observer=new IntersectionObserver((entries,observer)=>
    {
        entries.forEach((entry)=>
        {
            if(!entry.isIntersecting) return;
            const img=entry.target;
            const newUrl=img.getAttribute('data-src');
            img.src=newUrl;
            observer.unobserve(img);
        });
    },imgOpts);
  
    images.forEach((image)=>
    {
      observer.observe(image)
    });
}

$(document).ready(function()
{
  observerImages();
});

$(document).on('click','.btn-remove',function()
{
  $(this).parent().find('.loader-container').html(' <div class="overlay-loader">\
                                                      <svg class="circular" viewBox="25 25 50 50">\
                                                        <circle class="path" cx="50" cy="50" r="10" fill="none" stroke-width="2" stroke-miterlimit="10"/>\
                                                      </svg>\
                                                    </div>');
  $(this).parent().hide(); 
  return false;                                                
});

/*contact form*/
$(document).on('submit','.myForm',function()
{
  var el=$(this),
  btn_text=el.find('button span:last').text(),
  urlparams=new URLSearchParams(window.location.search),
  next=urlparams.get('next'),
  form_data=new FormData(this);
  el.children().find('.is-invalid').removeClass('is-invalid');
  $.ajax(
  {
    url:el.attr('action'),
    method:el.attr('method'),
    dataType:'json',
    data:form_data,
    contentType:false,
    cache:false,
    processData:false,
    beforeSend:function()
    {
      $(document).find('.feedback').html('');
      el.find('button span:first').html('<i class="spinner-border spinner-border-sm" role="status"></i>');
      el.find('button').attr('disabled',true);
      el.find('button span:last').text(' Please wait...');
    },
    success:function(callback)
    {
      el.find('button span:first').html('');
      el.find('button').attr('disabled',false);
      el.find('button span:last').text('SIGN IN');
      console.log(callback);
      if(!callback.valid)
      {
        $.each(callback.form_errors,function(prefix,value)
        {
          el.find("input[name='"+prefix+"'],textarea[name='"+prefix+"'],select[name='"+prefix+"']").addClass('is-invalid').parents('.form-group').find('.feedback').addClass('invalid-feedback').html('<i class="fa fa-exclamation-circle"></i> '+value[0]);
        });
      }
      else
      {
        if(next)
        {
            window.location=next;
        }
        else
        {
            window.location='/dashboard/';
        }
      }
    },
    error:function(err)
    {
      el.find('button span:first').html('');
      el.find('button').attr('disabled',false);
      el.find('button span:last').text('SIGN IN');
    }
  });
  return false;
});