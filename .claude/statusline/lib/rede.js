// HALCYON_STATUSLINE_OFFLINE=1 desliga toda chamada ao gh (consulta, atualizador destacado e mover).
// Os testes ligam isso para nunca tocar a rede nem um repo de verdade.
function semRede() {
  return process.env.HALCYON_STATUSLINE_OFFLINE === "1";
}

function exigirRede() {
  if (semRede()) throw new Error("HALCYON_STATUSLINE_OFFLINE=1: chamada ao gh bloqueada");
}

module.exports = { semRede, exigirRede };
