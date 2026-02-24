async function buscarItem(nomeItem) {
  // Monta a URL com o nome do item (encodeURIComponent cuida dos espaços/caracteres especiais)
  const url = `https://api.dofusdb.fr/items?slug.pt=${encodeURIComponent(nomeItem)}`;

  try {
    // 1. Faz a requisição
    const response = await fetch(url);

    // 2. Verifica se deu certo (status 200-299)
    if (!response.ok) {
      throw new Error(`Erro na requisição: ${response.status}`);
    }

    // 3. Converte o resultado de JSON para objeto JavaScript
    const data = await response.json();

    // 4. Usa os dados
    console.log(data);
    return data;

  } catch (error) {
    console.error('Algo deu errado:', error);
  }
}

buscarItem('potente menor');