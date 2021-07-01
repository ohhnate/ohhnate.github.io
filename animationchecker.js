function addAnimation() {
	const element = document.querySelector('.wrapper');
	element.classList.add('animate__animated', 'animate__bounceOutLeft');

	element.addEventListener('animationend', () => {
		window.location.href = "projects.html";
	});
}
$('#indexchange').click( function(e) {e.preventDefault(); return false; } );

//$('#indexchange').click(function(){ addAnimation(); return false; });