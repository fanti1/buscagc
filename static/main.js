
$(document).ready(function( )  {
	isRunning = false;
    $('#Form').on('submit', function(e){
    	e.preventDefault();

        var regx = /STEAM_[0-5]:[01]:\d+/g;
		var value = $('textarea[name=content]').val( );
		if ( regx.test( value ) )
		{
			isRunning = true;

			$( "#mut").toggle();
			$( "#loader" ).fadeIn( "slow" );
			$( "#loaded" ).show();
			$( "#change" ).text( "BUSCANDO..." );
			$( "#keke" ).prop("disabled", true);
			$( ".nav-items li a:first-child" ).attr("href", "javascript:void(0)");

			this.submit( );
		}
		else {
			$( "#asdf" ).toggle();
		}
    });

	handleFocus = function(){
		var $this = $(this);
		if($this.val() === $this.attr('placeholdernl')){
			$this.val('');
			$this.css('color', 'fff');
		}
	};

	handleBlur = function(){
		var $this = $(this);
		if($this.val() == ''){
			$this.val($this.attr('placeholdernl'))
			$this.css('color', '#57595a');
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