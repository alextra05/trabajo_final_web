// Definición de la URL de la API
const API_URL = "http://localhost:8000"

// ==========================================
// FUNCIONES AUXILIARES
// ==========================================

function getToken() {
  return localStorage.getItem("token")
}

function logout() {
  // Eliminar el token de localStorage
  localStorage.removeItem("token")
  localStorage.removeItem("user_role")
  sessionStorage.removeItem("remember_session")
  // Redirigir a la página principal
  window.location.href = "/"
}

function mostrarNotificacion(mensaje, tipo = "success") {
  const noti = document.createElement("div")
  noti.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm text-white ${
    tipo === "success" ? "bg-green-500" : tipo === "error" ? "bg-red-500" : "bg-blue-500"
  }`
  noti.textContent = mensaje
  document.body.appendChild(noti)
  setTimeout(() => document.body.removeChild(noti), 3000)
}

// Función para redirigir según el rol del usuario
function redirigirSegunRol(id_rol) {
  const rolId = Number.parseInt(id_rol, 10)
  switch (rolId) {
    case 1:
      // Redirigir al supervisor
      window.location.href = "/super"
      break
    case 2:
      // Redirigir al administrador
      window.location.href = "/admin"
      break
    case 3:
      // Redirigir al usuario regular
      window.location.href = "/"
      break
    default:
      // En caso de un rol no reconocido
      console.error("Rol no reconocido:", rolId)
      window.location.href = "/"
      break
  }
}

// ==========================================
// FUNCIÓN DE VERIFICACIÓN DE SESIÓN
// ==========================================

// Verificar si hay sesión activa
function checkSession() {
  // Si la página actual ha indicado que debemos omitir esta verificación
  if (window.skipGlobalSessionCheck) {
    console.log("Omitiendo verificación global de sesión")
    return
  }

  const token = getToken()
  const currentPath = window.location.pathname

  // Verificar si estamos en una página de admin o super
  const isAdminPage = currentPath === "/admin" || currentPath === "/admin.html"
  const isSuperPage = currentPath === "/super" || currentPath === "/super.html"

  if (!token) {
    console.log("No hay token almacenado")
    // Asegurarse de que los botones de autenticación estén visibles
    document.getElementById("auth-buttons-desktop")?.classList.remove("hidden")
    document.getElementById("auth-buttons-mobile")?.classList.remove("hidden")
    document.getElementById("perfil-wrapper-desktop")?.classList.add("hidden")
    document.getElementById("perfil-options-mobile")?.classList.add("hidden")

    // También actualizar los elementos de la barra de navegación principal si existen
    document.getElementById("login-link")?.classList.remove("hidden")
    document.getElementById("register-link")?.classList.remove("hidden")
    document.getElementById("perfil-wrapper")?.classList.add("hidden")

    // Si estamos en una página protegida, redirigir al login
    if (isAdminPage || isSuperPage) {
      window.location.href = "/login"
    }

    return
  }

  // Realizamos la petición al backend para obtener los datos del usuario
  fetch(`${API_URL}/usuarios/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/json",
    },
  })
    .then((res) => {
      if (!res.ok) {
        if (res.status === 401) {
          throw new Error("Token inválido o expirado")
        }
        throw new Error("No hay sesión activa")
      }
      return res.json()
    })
    .then((user) => {
      console.log("Usuario autenticado:", user)

      // Actualizar el rol almacenado en localStorage
      if (user.id_rol) {
        localStorage.setItem("user_role", user.id_rol.toString())
      }

      // Verificar si el usuario debería estar en la página actual
      const userRole = user.id_rol
      const shouldBeInAdminPage = userRole === 1 || userRole === 2
      const shouldBeInSuperPage = userRole === 1

      // Verificar acceso a páginas protegidas SOLO si no estamos ya en ellas
      if (isAdminPage && !shouldBeInAdminPage) {
        mostrarNotificacion("No tienes permisos para acceder a esta página", "error")
        window.location.href = "/"
      } else if (isSuperPage && !shouldBeInSuperPage) {
        mostrarNotificacion("No tienes permisos para acceder a esta página", "error")
        window.location.href = "/"
      }

      // Mostrar elementos de perfil y ocultar botones de autenticación
      const authButtonsDesktop = document.getElementById("auth-buttons-desktop")
      const authButtonsMobile = document.getElementById("auth-buttons-mobile")
      const perfilWrapperDesktop = document.getElementById("perfil-wrapper-desktop")
      const perfilOptionsMobile = document.getElementById("perfil-options-mobile")

      if (authButtonsDesktop) authButtonsDesktop.classList.add("hidden")
      if (authButtonsMobile) authButtonsMobile.classList.add("hidden")
      if (perfilWrapperDesktop) perfilWrapperDesktop.classList.remove("hidden")
      if (perfilOptionsMobile) perfilOptionsMobile.classList.remove("hidden")

      // También actualizar los elementos de la barra de navegación principal si existen
      const loginLink = document.getElementById("login-link")
      const registerLink = document.getElementById("register-link")
      const perfilWrapper = document.getElementById("perfil-wrapper")

      if (loginLink) loginLink.classList.add("hidden")
      if (registerLink) registerLink.classList.add("hidden")
      if (perfilWrapper) perfilWrapper.classList.remove("hidden")

      // Actualizar la inicial del perfil si existe
      const perfilInicial = document.getElementById("perfil-inicial")
      if (perfilInicial && user.nombre) {
        perfilInicial.textContent = user.nombre.charAt(0).toUpperCase()
      }

      // Actualizar la imagen de perfil con la inicial del usuario si no hay imagen
      const avatarImgs = document.querySelectorAll(".avatar-img")
      avatarImgs.forEach((img) => {
        // Si hay una URL de imagen de perfil en el usuario, usarla
        if (user.imagen_perfil) {
          img.src = user.imagen_perfil
        } else {
          // Si no hay imagen, generar un avatar con la inicial del usuario
          const nombre = encodeURIComponent(user.nombre || "Usuario")
          img.src = `https://ui-avatars.com/api/?name=${nombre}&background=random&color=fff`
        }
      })
    })
    .catch((err) => {
      console.log("Error de sesión:", err.message)
      // Si hay error, limpiar el token y el rol
      localStorage.removeItem("token")
      localStorage.removeItem("user_role")
      // Asegurarse de que los botones de autenticación estén visibles
      document.getElementById("auth-buttons-desktop")?.classList.remove("hidden")
      document.getElementById("auth-buttons-mobile")?.classList.remove("hidden")
      document.getElementById("perfil-wrapper-desktop")?.classList.add("hidden")
      document.getElementById("perfil-options-mobile")?.classList.add("hidden")

      // También actualizar los elementos de la barra de navegación principal si existen
      document.getElementById("login-link")?.classList.remove("hidden")
      document.getElementById("register-link")?.classList.remove("hidden")
      document.getElementById("perfil-wrapper")?.classList.add("hidden")

      // Si estamos en una página protegida, redirigir al login
      if (isAdminPage || isSuperPage) {
        mostrarNotificacion("Sesión inválida. Por favor inicia sesión nuevamente.", "error")
        window.location.href = "/login"
      }
    })
}

// ==========================================
// FUNCIONES DE CURSOS
// ==========================================

// Función para inscribirse a un curso
function inscribirseCurso(cursoId) {
  const token = getToken()
  if (!token) {
    // Si no está autenticado, redirigir al login
    window.location.href = `/login?next=/curso/${cursoId}`
    return
  }

  // Hacer la petición para inscribirse
  fetch(`${API_URL}/usuarios/inscribirse/${cursoId}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      Accept: "application/json",
    },
  })
    .then((res) => {
      if (!res.ok) {
        if (res.status === 400) {
          return res.json().then((data) => {
            throw new Error(data.detail || "Ya estás inscrito en este curso")
          })
        }
        throw new Error("Error al inscribirse al curso")
      }
      return res.json()
    })
    .then((data) => {
      mostrarNotificacion("¡Te has inscrito correctamente al curso!", "success")
      // Recargar la página para actualizar la información
      window.location.reload()
    })
    .catch((err) => {
      mostrarNotificacion(err.message, "error")
    })
}

// Función para verificar si ya está inscrito en un curso
async function verificarInscripcion(cursoId) {
  const token = getToken()
  if (!token) return false

  try {
    const res = await fetch(`${API_URL}/usuarios/mis-cursos`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) return false
    const cursos = await res.json()
    return cursos.some((curso) => curso.id === Number.parseInt(cursoId))
  } catch {
    return false
  }
}

// Función para cargar cursos destacados
function loadFeaturedCourses() {
  const token = getToken()

  fetch(`${API_URL}/cursos`, {
    headers: {
      Accept: "application/json",
      Authorization: token ? `Bearer ${token}` : "",
    },
  })
    .then((res) => res.json())
    .then((cursos) => {
      const container = document.getElementById("cursos-container")

      if (!cursos || cursos.length === 0) {
        container.innerHTML =
          '<p class="text-center col-span-full">No hay cursos destacados disponibles en este momento.</p>'
        return
      }

      // Mostrar solo los primeros 3-6 cursos
      const cursosAMostrar = cursos.slice(0, 6)

      container.innerHTML = cursosAMostrar
        .map(
          (curso) => `
      <div class="curso-card bg-white rounded-xl shadow-md overflow-hidden relative">
        <div class="h-48 bg-gray-200 relative">
          ${
            curso.imagen
              ? `<img src="${curso.imagen}" alt="${curso.nombre}" class="w-full h-full object-cover">`
              : `<div class="w-full h-full flex items-center justify-center text-gray-400">
                 <i class="fas fa-laptop-code text-4xl"></i>
               </div>`
          }
          ${curso.destacado ? '<span class="badge badge-popular">Popular</span>' : ""}
          ${curso.nuevo ? '<span class="badge badge-nuevo">Nuevo</span>' : ""}
        </div>
        <div class="p-6">
          <h3 class="font-bold text-xl mb-2">${curso.nombre}</h3>
          <p class="text-gray-600 mb-4">${curso.descripcion?.substring(0, 100) || "Sin descripción"}${curso.descripcion?.length > 100 ? "..." : ""}</p>
          
          <!-- Botón de inscripción -->
          <button onclick="inscribirseCurso(${curso.id})" class="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition mb-4">
            Inscribirme
          </button>
          
          <!-- Personas inscritas -->
          <div class="flex justify-between items-center
          ">
              <div class="flex items-center">
                <span class="text-gray-600 mr-2">Personas</span>
                <div class="flex items-center">
                  <span class="inline-flex items-center">
                    <i class="fas fa-user-circle text-gray-400 mr-1"></i>
                    <span class="text-gray-600">${curso.inscritos || 0}</span>
                  </span>
                </div>
              </div>
              <button onclick="verPersonas(${curso.id})" class="text-blue-600 font-medium hover:underline">
                Ver personas
              </button>
            </div>
          </div>
        </div>
      `,
        )
        .join("")
    })
    .catch((err) => {
      console.error("Error al cargar cursos:", err)
      const container = document.getElementById("cursos-container")
      container.innerHTML =
        '<p class="text-center col-span-full">Error al cargar los cursos. Inténtalo de nuevo más tarde.</p>'
    })
}

// Función para mostrar los usuarios inscritos en un curso
function verPersonas(cursoId) {
  const modal = document.getElementById("usuarios-modal")
  const modalTitle = document.getElementById("modal-title")
  const modalContent = document.getElementById("modal-content")
  const token = getToken()

  // Mostrar el modal con un loader
  modal.classList.remove("hidden")
  modalContent.innerHTML =
    '<div class="flex justify-center py-8"><i class="fas fa-spinner fa-spin text-3xl text-blue-600"></i></div>'

  // Obtener los usuarios inscritos en el curso
  fetch(`${API_URL}/cursos/${cursoId}/participantes`, {
    headers: {
      Accept: "application/json",
      Authorization: token ? `Bearer ${token}` : "",
    },
  })
    .then((res) => {
      if (!res.ok) throw new Error("Error al obtener los usuarios")
      return res.json()
    })
    .then((usuarios) => {
      modalTitle.textContent = `Usuarios inscritos (${usuarios.length})`

      if (usuarios.length === 0) {
        modalContent.innerHTML =
          '<p class="text-center py-4 text-gray-500">No hay usuarios inscritos en este curso.</p>'
        return
      }

      // Crear la lista de usuarios
      const usuariosHTML = usuarios
        .map(
          (usuario) => `
      <div class="flex items-center gap-3 py-2 border-b border-gray-100">
        <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold">
          ${usuario.nombre?.charAt(0)?.toUpperCase() || "U"}
        </div>
        <div>
          <p class="font-medium">${usuario.nombre} ${usuario.apellidos || ""}</p>
          <p class="text-sm text-gray-500">${usuario.email}</p>
        </div>
      </div>
    `,
        )
        .join("")

      modalContent.innerHTML = usuariosHTML
    })
    .catch((err) => {
      modalContent.innerHTML = `<p class="text-center py-4 text-red-500">${err.message}</p>`
    })
}

// Función para cerrar el modal
function cerrarModal() {
  const modal = document.getElementById("usuarios-modal")
  modal.classList.add("hidden")
}

// ==========================================
// FUNCIONES DE LOGIN/AUTENTICACIÓN
// ==========================================

// Función para verificar y validar el token en la página de login
function checkLoginToken() {
  const token = getToken()
  if (token) {
    try {
      // Verificar si el token es válido
      fetch(`${API_URL}/usuarios/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
      })
        .then((res) => {
          if (res.ok) {
            // Si el token es válido, obtener los datos del usuario
            return res.json()
          } else {
            // Si el token no es válido, eliminarlo
            localStorage.removeItem("token")
            localStorage.removeItem("user_role")
            throw new Error("Token inválido")
          }
        })
        .then((userData) => {
          // Redirigir según el rol del usuario
          if (userData && userData.id_rol) {
            redirigirSegunRol(userData.id_rol)
          } else {
            // Si no hay rol definido, redirigir a la página principal
            window.location.href = "/"
          }
        })
        .catch((error) => {
          console.error("Error al verificar sesión:", error)
          localStorage.removeItem("token")
          localStorage.removeItem("user_role")
        })
    } catch (error) {
      console.error("Error al verificar sesión:", error)
      localStorage.removeItem("token")
      localStorage.removeItem("user_role")
    }
  }
}

// Función para manejar el formulario de login
function setupLoginForm() {
  const loginForm = document.getElementById("login-form")
  const errorMsg = document.getElementById("error-msg")

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault()
      const username = document.getElementById("username").value
      const password = document.getElementById("password").value
      const remember = document.getElementById("remember").checked

      try {
        const res = await fetch(`${API_URL}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({ username, password }),
        })

        if (res.ok) {
          const data = await res.json()
          localStorage.setItem("token", data.access_token)

          // Si el usuario marcó "recordar", guardar también en sessionStorage
          if (remember) {
            sessionStorage.setItem("remember_session", "true")
          }

          // Guardar el id_rol en localStorage para acceso rápido
          if (data.id_rol) {
            localStorage.setItem("user_role", data.id_rol.toString())
            redirigirSegunRol(data.id_rol)
          } else if (data.usuario && data.usuario.id_rol) {
            localStorage.setItem("user_role", data.usuario.id_rol.toString())
            redirigirSegunRol(data.usuario.id_rol)
          } else {
            // Si no hay id_rol en la respuesta, hacer una solicitud adicional
            const userRes = await fetch(`${API_URL}/usuarios/me`, {
              headers: {
                Authorization: `Bearer ${data.access_token}`,
                Accept: "application/json",
              },
            })

            if (userRes.ok) {
              const userData = await userRes.json()
              if (userData && userData.id_rol) {
                localStorage.setItem("user_role", userData.id_rol.toString())
                redirigirSegunRol(userData.id_rol)
              } else {
                // Si no hay rol definido, redirigir a la página principal
                window.location.href = "/"
              }
            } else {
              // Si hay error al obtener datos del usuario, redirigir a la página principal
              window.location.href = "/"
            }
          }
        } else {
          const errorData = await res.json()
          if (errorMsg) {
            errorMsg.textContent = errorData.detail || "Credenciales incorrectas."
            errorMsg.classList.remove("hidden")
          } else {
            mostrarNotificacion(errorData.detail || "Error de autenticación", "error")
          }
        }
      } catch (error) {
        console.error("Error de conexión:", error)
        if (errorMsg) {
          errorMsg.textContent = "Error de conexión."
          errorMsg.classList.remove("hidden")
        } else {
          mostrarNotificacion("Error de conexión", "error")
        }
      }
    })
  }
}

// ==========================================
// CONFIGURACIÓN DE EVENTOS UI
// ==========================================

// Inicializar funcionalidades UI
function setupUI() {
  // Menú móvil
  document.getElementById("mobile-menu-button")?.addEventListener("click", () => {
    document.getElementById("mobile-menu")?.classList.toggle("hidden")
  })

  // Menú perfil (Desktop)
  document.getElementById("perfil-btn-desktop")?.addEventListener("click", () => {
    document.getElementById("perfil-dropdown-desktop")?.classList.toggle("hidden")
  })

  // Menú perfil (Navbar principal)
  document.getElementById("perfil-btn")?.addEventListener("click", () => {
    document.getElementById("perfil-dropdown")?.classList.toggle("hidden")
  })

  // Cerrar dropdown al hacer clic fuera
  document.addEventListener("click", (e) => {
    // Cerrar dropdown desktop
    const btnDesktop = document.getElementById("perfil-btn-desktop")
    const dropdownDesktop = document.getElementById("perfil-dropdown-desktop")
    if (btnDesktop && dropdownDesktop && !btnDesktop.contains(e.target) && !dropdownDesktop.contains(e.target)) {
      dropdownDesktop.classList.add("hidden")
    }

    // Cerrar dropdown navbar principal
    const btn = document.getElementById("perfil-btn")
    const dropdown = document.getElementById("perfil-dropdown")
    if (btn && dropdown && !btn.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.classList.add("hidden")
    }
  })

  // Configurar eventos para el modal
  document.getElementById("close-modal")?.addEventListener("click", cerrarModal)
  document.getElementById("modal-close-btn")?.addEventListener("click", cerrarModal)

  // Cerrar modal al hacer clic fuera
  document.getElementById("usuarios-modal")?.addEventListener("click", function (e) {
    if (e.target === this) {
      cerrarModal()
    }
  })

  // Manejar el formulario de suscripción
  document.getElementById("subscription-form")?.addEventListener("submit", function (e) {
    e.preventDefault()
    const email = this.querySelector('input[type="email"]').value
    mostrarNotificacion(`Gracias por suscribirte con ${email}! Te contactaremos pronto.`, "success")
    this.reset()
  })

  // Configurar botones de logout
  document.querySelectorAll(".logout-btn").forEach((btn) => {
    btn.addEventListener("click", logout)
  })
}

// ==========================================
// INICIALIZACIÓN GENERAL
// ==========================================

// Cuando el DOM esté cargado, inicializar la aplicación
document.addEventListener("DOMContentLoaded", () => {
  // Comprobar la URL actual para determinar la página
  const currentPath = window.location.pathname

  // Configuración común para todas las páginas
  setupUI()

  // Configuración específica según la página
  if (currentPath === "/login" || currentPath === "/login.html") {
    // Configuración específica para la página de login
    checkLoginToken()
    setupLoginForm()
  } else if (
    currentPath === "/admin" ||
    currentPath === "/admin.html" ||
    currentPath === "/super" ||
    currentPath === "/super.html"
  ) {
    // Para páginas protegidas, verificar autenticación primero
    const token = getToken()
    if (!token) {
      mostrarNotificacion("Debes iniciar sesión para acceder a esta página", "error")
      window.location.href = "/login"
      return
    }

    // Para admin y super, NO ejecutamos checkSession() aquí
    // En su lugar, cada página tendrá su propio script específico

    // Establecer la bandera para evitar que checkSession() global redirija
    window.skipGlobalSessionCheck = true
  } else {
    // Para todas las demás páginas (incluido index)
    checkSession()

    // Si es la página principal, cargar los cursos
    if (currentPath === "/" || currentPath === "/index" || currentPath === "/index.html" || currentPath === "/inicio" || currentPath === "/inicio.html") {
      const cursosContainer = document.getElementById("cursos-container")
      if (cursosContainer) {
        loadFeaturedCourses()
      }
    }
  }
})