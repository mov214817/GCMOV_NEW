console.log('dentro cargacombo.js');
/*const url = '/get_state/';*/
const url = '/get_regiones/';


cargarCombo('cmbregion', '/get_regiones/');  // Trae regiones al cargar la página

async function cargarCombo(comboId, url) {
    console.log(`Ejecutando cargarCombo para ${comboId}...`);
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Error al obtener datos del servidor');

        const datos = await response.json();
        const select = document.getElementById(comboId);
        if (!select) throw new Error(`El elemento <select> con ID ${comboId} no se encontró en el DOM.`);

       // select.innerHTML = '<option value="" selected>Seleccione</option>';
        datos.forEach(item => {
            const option = document.createElement('option');

            if (comboId === 'cmbregion') {
                option.value = item.idregion;
                option.textContent = item.region_name;
            } else if (comboId === 'cmbstate') {
                option.value = item.id_state;
                option.textContent = item.state_name;
            }

            select.appendChild(option);
        });
        console.log(`Combo ${comboId} actualizado con los datos del backend.`);
    } catch (error) {
        console.error(`Error en cargarCombo para ${comboId}:`, error);
    }
}

async function cargarEstados() {
    const regionId = document.getElementById("cmbregion").value;
    const estadoSelect = document.getElementById("cmbstate");
    const ciudadSelect = document.getElementById("cmbciud");
/*
    if (!regionId) {
        estadoSelect.innerHTML = '<option value="" selected>Seleccione un estado</option>';
        ciudadSelect.innerHTML = '<option value="" selected>Seleccione una ciudad</option>';
        return;
    }
*/
    try {
        const response = await fetch(`/get_state/${regionId}`);
        if (!response.ok) throw new Error("Error al obtener estados por región");

        const datos = await response.json();
      /*  estadoSelect.innerHTML = '<option value="" selected>Seleccione un estado</option>';
        ciudadSelect.innerHTML = '<option value="" selected>Seleccione una ciudad</option>';
*/
        datos.forEach(item => {
            const option = document.createElement("option");
            option.value = item.id_state;
            option.textContent = item.state_name;
            estadoSelect.appendChild(option);
        });

        console.log(`Estados cargados para la región ${regionId}`);
    } catch (error) {
        console.error("Error al cargar estados:", error);
    }
}

// Función para cargar ciudades cuando cambia el estado
async function cargarCiudades() {
    const estadoSelect = document.getElementById("cmbstate");
    const ciudadSelect = document.getElementById("cmbciud");
    
    const estadoId = estadoSelect.value; // Obtiene el ID del estado seleccionado
    console.log('Estado seleccionado:', estadoId);

    // Si no hay estado seleccionado, limpia el select de ciudades
  /*  if (!estadoId) {
        ciudadSelect.innerHTML = '<option value="" selected>Seleccione</option>';
        return;
    }
*/
    try {
        // 🔹 Corrección: URL sin interpolación incorrecta
       const response = await fetch(`/get_ciudad/${estadoId}`);


        if (!response.ok) throw new Error("Error al obtener ciudades");

        const datos = await response.json();
       // ciudadSelect.innerHTML = '<option value="" selected>Seleccione una ciudad</option>';

        datos.forEach(item => {
            const option = document.createElement("option");
            option.value = item.id_ciudad;
            option.textContent = item.ciudad_name;
            ciudadSelect.appendChild(option);
        });

        console.log(`Ciudades cargadas para el estado ${estadoId}`);
    } catch (error) {
        console.error("Error al cargar ciudades:", error);
    }
}


document.addEventListener("DOMContentLoaded", () => {
  const { idregion, idstate, idciudad, existe } = window.datosCliente;
  const cmbregion = document.getElementById("cmbregion");
  const cmbstate = document.getElementById("cmbstate");
  const cmbciud = document.getElementById("cmbciud");

  if (!cmbregion || !cmbstate || !cmbciud) {
    console.error("❌ No se encontraron los combos requeridos.");
    return;
  }

  // 🔹 Cargar regiones
  fetch("/get_regiones/")
    .then(res => res.json())
    .then(regiones => {
      cmbregion.innerHTML = '<option value="">Seleccione</option>';
      regiones.forEach(r => {
        const opt = new Option(r.region_name, r.idregion);
        if (String(r.idregion) === String(idregion)) opt.selected = true;
        cmbregion.appendChild(opt);
      });

      if (existe && idregion) cargarEstados(idregion);
    })
    .catch(err => console.error("Error al cargar regiones:", err));

  // 🔹 Evento cambio región → cargar estados
  cmbregion.addEventListener("change", () => {
    const nuevaRegionId = cmbregion.value;
    cargarEstados(nuevaRegionId);
  });

  // 🔹 Evento cambio estado → cargar ciudades
  cmbstate.addEventListener("change", () => {
    const nuevoEstadoId = cmbstate.value;
    cargarCiudades(nuevoEstadoId);
  });

  // 🔹 Si ya hay valores, podés forzar carga directa
  if (existe && idstate && !idregion) {
    cargarEstados(null); // Si tenés región vacía pero estado desde BD
  }
});

function cargarEstados(regionId) {
  const { idstate, existe } = window.datosCliente;
  const cmbstate = document.getElementById("cmbstate");

  if (!cmbstate || !regionId) return;

  fetch(`/get_state/${regionId}/`)
    .then(res => res.json())
    .then(estados => {
      cmbstate.innerHTML = '<option value="">Seleccione</option>';
      estados.forEach(e => {
        const opt = new Option(e.state_name, e.id_state);
        if (String(e.id_state) === String(idstate)) opt.selected = true;
        cmbstate.appendChild(opt);
      });

      if (existe && idstate) cargarCiudades(idstate);
    })
    .catch(err => console.error("Error al cargar estados:", err));
}

function cargarCiudades(stateId) {
  const { idciudad } = window.datosCliente;
  const cmbciud = document.getElementById("cmbciud");

  if (!cmbciud || !stateId) return;

  fetch(`/get_ciudad/${stateId}/`)
    .then(res => res.json())
    .then(ciudades => {
      cmbciud.innerHTML = '<option value="">Seleccione</option>';
      ciudades.forEach(c => {
        const opt = new Option(c.ciudad_name, c.id_ciudad);
        if (String(c.id_ciudad) === String(idciudad)) opt.selected = true;
        cmbciud.appendChild(opt);
      });
    })
    .catch(err => console.error("Error al cargar ciudades:", err));
}
