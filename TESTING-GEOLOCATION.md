# Testando Geolocalização e Movimento - Guia Completo

## 🎯 Objetivo
Simular movimento do usuário para testar o fluxo completo de navegação com áudio em tempo real.

---

## 📋 Opção 1: Chrome DevTools (Mais Fácil)

### Passos:
1. Abra a aplicação NaviAcess (http://localhost:5173)
2. Abra DevTools com **F12**
3. Vá para **More tools → Sensors** (ou pesquise "Sensors" no Command Palette)
4. Localize a seção **Location**
5. Selecione **Custom location**
6. Defina coordenadas e clique em **Overrides**

### Coordenadas para testar:
```
Origem (Lisbon):        38.7307129, -9.1299245
Destino (Carcavelos):   38.6792232, -9.3352361
Ponto intermediário 1:   38.7300000, -9.1300000
Ponto intermediário 2:   38.7290000, -9.1310000
Ponto intermediário 3:   38.7200000, -9.1400000
```

### Como funciona:
- Chrome vai simular essa localização no `navigator.geolocation`
- Sua app receberá como se fosse locais reais
- Mude as coordenadas manualmente para simular movimento

---

## 🛠️ Opção 2: JavaScript Console (Automático)

### Carregue o mock helper:
No console do navegador, execute:

```javascript
// Importar o helper (se estiver usando ES modules)
import { setupGeolocationMock } from './utils/geolocationMock.js';
setupGeolocationMock();
```

Ou, mais simples, adicione no seu `App.jsx`:

```jsx
import { useEffect } from 'react';
import { setupGeolocationMock } from './utils/geolocationMock';

function App() {
  useEffect(() => {
    // Ativar mock apenas em desenvolvimento
    if (process.env.NODE_ENV === 'development') {
      setupGeolocationMock();
    }
  }, []);

  return (
    // ... resto do código
  );
}
```

### Comandos disponíveis no console:

```javascript
// Iniciar simulação automática (atualiza a cada 5 segundos)
startGeolocationSimulation();

// Iniciar com intervalo customizado (em ms)
startGeolocationSimulation(3000); // atualiza a cada 3 segundos

// Parar simulação
stopGeolocationSimulation();

// Resetar para o início
resetGeolocationSimulation();

// Ir para um passo específico
jumpToStep(3); // Pula para o 3º waypoint

// Ver status atual
getSimulationStatus();
// Output:
// {
//   isRunning: true,
//   currentStep: 3,
//   totalSteps: 6,
//   progress: "2/6"
// }
```

### Exemplo completo de teste:

```javascript
// 1. Iniciar simulação
startGeolocationSimulation(2000); // atualiza a cada 2s

// 2. Assistir os logs:
// 📍 Step 1/6: 38.7307, -9.1299
//    📢 "Starting point"
//
// 📍 Step 2/6: 38.7300, -9.1300
//    📢 "Walking north"
// ... (continua)

// 3. Parar quando quiser
stopGeolocationSimulation();
```

---

## 🧪 Opção 3: Testes Vitest (Automatizado)

Execute os testes de geolocalização:

```bash
cd frontend
npm test src/tests/useGeolocation.test.jsx
```

### Exemplo de teste que simula movimento:

```javascript
it('should update location when position changes', async () => {
  const initialPosition = {
    coords: {
      latitude: 38.7307129,
      longitude: -9.1299245,
    },
  };

  const updatedPosition = {
    coords: {
      latitude: 38.7320000,
      longitude: -9.1310000,
    },
  };

  // Simula movimento do Lisbon para... um pouco mais ao norte
  watchCallback(updatedPosition);

  // Verifica se a localização foi atualizada
  expect(result.current.location.latitude).toBe(38.7320000);
});
```

---

## 🌐 Opção 4: Teste E2E com Cypress

Crie arquivo `frontend/cypress/e2e/geolocation.cy.js`:

```javascript
describe('Geolocation Navigation', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5173');
  });

  it('should track user movement and update route', () => {
    // Simular posição inicial
    cy.window().then((win) => {
      cy.stub(win.navigator.geolocation, 'getCurrentPosition').callsFake(
        (success) => {
          success({
            coords: {
              latitude: 38.7307129,
              longitude: -9.1299245,
              accuracy: 10,
            },
          });
        }
      );
    });

    // Verificar que a localização foi obtida
    cy.contains('38.7307129').should('be.visible');

    // Simular movimento
    cy.window().then((win) => {
      const watchCallbacks = [];
      cy.stub(win.navigator.geolocation, 'watchPosition').callsFake(
        (success) => {
          watchCallbacks.push(success);
          return 1;
        }
      );

      // Disparar atualização de posição
      watchCallbacks.forEach((cb) => {
        cb({
          coords: {
            latitude: 38.7320000,
            longitude: -9.1310000,
            accuracy: 10,
          },
        });
      });
    });

    // Verificar que a posição foi atualizada
    cy.contains('38.7320000').should('be.visible');
  });
});
```

Execute com:
```bash
npx cypress open
```

---

## 🎮 Opção 5: Aplicação Interativa (Ideal para Dev)

Use arquivo `geolocationMock.js` para criar um painel de controle:

```jsx
// MyDebugPanel.jsx
import { useState } from 'react';
import * as geolocationMock from '../utils/geolocationMock';

export function DebugPanel() {
  const [isRunning, setIsRunning] = useState(false);
  const [step, setStep] = useState(1);

  return (
    <div style={{ border: '2px solid red', padding: '10px', margin: '10px' }}>
      <h3>🧪 Debug Geolocation</h3>

      <button
        onClick={() => {
          if (!isRunning) {
            window.startGeolocationSimulation(2000);
            setIsRunning(true);
          }
        }}
      >
        ▶️ Começar Simulação
      </button>

      <button
        onClick={() => {
          window.stopGeolocationSimulation();
          setIsRunning(false);
        }}
      >
        ⏹️ Parar
      </button>

      <button onClick={() => window.resetGeolocationSimulation()}>
        🔄 Reset
      </button>

      <input
        type="number"
        min="1"
        max="6"
        value={step}
        onChange={(e) => setStep(Number(e.target.value))}
      />

      <button onClick={() => window.jumpToStep(step)}>
        ⏩ Ir para passo {step}
      </button>

      <pre>{JSON.stringify(window.getSimulationStatus(), null, 2)}</pre>
    </div>
  );
}
```

Adicione ao `App.jsx`:

```jsx
import { DebugPanel } from './components/DebugPanel';

function App() {
  return (
    <>
      {process.env.NODE_ENV === 'development' && <DebugPanel />}
      {/* resto da app */}
    </>
  );
}
```

---

## 📊 Fluxo de Teste Completo

### 1️⃣ **Inicializar**
```javascript
startGeolocationSimulation(5000); // atualiza a cada 5 segundos
```

### 2️⃣ **Observar**
- Veja os logs do console mostrando movimento
- Verifique se o mapa atualiza
- Escute os áudios de instrução tocando

### 3️⃣ **Monitorar Backend**
```bash
# Em outro terminal
docker logs naviacess-backend -f
```

Procure por:
```
INFO:     172.20.0.1:52202 - "POST /api/update-location HTTP/1.1" 200 OK
```

### 4️⃣ **Validar Fluxo End-to-End**
- ✅ Usuário fala destino
- ✅ Rota é calculada
- ✅ Áudio inicial toca
- ✅ Primeiro passo toca
- ✅ Simulação de movimento começa
- ✅ Próximos passos tocam automaticamente
- ✅ Chegada é anunciada

---

## 🎯 Coordenadas Pré-configuradas

### Rota 1: Lisbon → Carcavelos (Praia)
```
Origem:      38.7307129, -9.1299245
Destino:     38.6792232, -9.3352361
Distância:   ~18 km
Tempo:       ~3 horas a pé
```

### Rota 2: City Center → Park (mais curta)
```
Origem:      38.7100000, -9.1400000
Destino:     38.7200000, -9.1200000
Distância:   ~2 km
Tempo:       ~25 minutos
```

---

## ⚠️ Troubleshooting

### Mock não funciona
**Causa:** `navigator.geolocation` é read-only em produção  
**Solução:** Use DevTools Sensors ou rode em modo desenvolvimento

### Simulação parou
**Verifique:**
```javascript
getSimulationStatus(); // Mostra se está rodando
window.geolocationSimulationInterval; // Deve ter um número
```

### Áudio não toca
**Verifique:**
1. Console de erros do navegador
2. Backend logs: `docker logs naviacess-backend`
3. CORS está habilitado no backend?

### 404 nos arquivos de áudio
**Solução:** Verifique se `/api/speak-initial` e `/api/speak-step` estão respondendo

---

## 🚀 Resumo Rápido

| Opção | Facilidade | Automação | Melhor para |
|-------|-----------|-----------|------------|
| **DevTools Sensors** | ⭐⭐⭐ | ❌ | Testes manuais rápidos |
| **Console Mock** | ⭐⭐ | ⭐⭐⭐ | Desenvolvimento |
| **Vitest** | ⭐ | ⭐⭐⭐ | CI/CD |
| **Cypress** | ⭐⭐ | ⭐⭐⭐ | E2E completo |
| **Debug Panel** | ⭐⭐⭐ | ⭐⭐ | Teste interativo |

---

**Qual você quer testar primeiro? 🤔**
