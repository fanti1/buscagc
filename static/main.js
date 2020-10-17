
$(document).ready(function( )  {
	var isRunning = false;
	var sending = false;
	let textareavalue = $("textarea[name=content]").value;
	$( '#ajaxx' ).click( function( ) {
		if ( sending == true )
		{
			isRunning = true;
			$( "#loader" ).fadeIn( "slow" );
			$( "#mut").toggle();

			$( "#change" ).text( "BUSCANDO" );
			$( "#keke" ).prop("disabled", true);
			$('.nav-items li a:first-child').attr("href", "javascript:void(0)");
		}

	});

	handleFocus = function(){
		var $this = $(this);
		if($this.val() === $this.attr('placeholdernl')){
			$this.val('');
			$this.css('color', '');
		}
	};

	handleBlur = function(){
		var $this = $(this);
		if($this.val() == ''){
			$this.val($this.attr('placeholdernl'))
			$this.css('color', 'gray');
		}
	};

	$('textarea[placeholdernl]').each(function(){
		var $this = $(this),
			value = $this.val(),
			placeholder = $this.attr('placeholder');
		$this.attr('placeholdernl', value ? value : placeholder);
		$this.val('');
		$this.focus(handleFocus).blur(handleBlur).trigger('blur');
	});

	$( '#change' ).click( function( ) {
		if ( isRunning == false ) {
			$(this).text((i, t) => t == 'PESQUISAR MINHA PARTIDA' ? 'VOLTAR' : 'PESQUISAR MINHA PARTIDA');
			$('#mut, #teste, .card-container, .h').toggle();
		}
	});
});

function Check( )
{
	var regx = /STEAM_[0-5]:[01]:\d+/g;
	var value = $('textarea[name=content]').val( );
	if ( regx.test( value ) )
	{
		sending = true;
		return true;
	}
	else
	{
		sending = false;
		return false;
	}
}
