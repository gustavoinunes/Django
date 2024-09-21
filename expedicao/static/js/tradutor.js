const translations = {
    en: {
        import: "Welcome to My Website",
        description: "This is an example of a dynamic translation page."
    },
    es: {
        import: "Bienvenido a Mi Sitio Web",
        description: "Este es un ejemplo de una página de traducción dinámica."
    }
};

function setLanguage(es) {
    document.getElementById('import').innerText = translations[es].import;
    document.getElementById('description').innerText = translations[es].description;
}