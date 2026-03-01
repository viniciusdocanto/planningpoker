import { test, expect } from '@playwright/test';

test('fluxo completo: criar sala, votar, revelar e resetar', async ({ page }) => {
    // 1. Acessar a home
    await page.goto('/');
    await expect(page).toHaveTitle(/Planning Poker/);

    // 2. Criar uma nova sala
    await page.getByPlaceholder('Como devemos te chamar?').fill('Test User');
    await page.getByText('✨ Criar nova sala').click();

    // 3. Verificar se entrou na sala (URL deve conter /room/)
    await expect(page).toHaveURL(/.*\/room\/.*/);

    // Esperar o status de conexão (OK)
    await expect(page.getByText('OK')).toBeVisible();

    // O usuário deve aparecer na lista como "Você"
    await expect(page.getByText('Você')).toBeVisible();

    // 4. Votar (escolher a carta '5')
    // Usamos um locator mais robusto para a carta
    const cardFive = page.locator('button').filter({ hasText: /^5$/ });
    await cardFive.click();

    // Verificar se o status mudou para "Votou" para o usuário
    await expect(page.getByText('Votou')).toBeVisible({ timeout: 10000 });

    // 5. Revelar votos (como fomos o criador, somos o host)
    const revealButton = page.getByRole('button', { name: 'Revelar' });
    await revealButton.click();

    // Verificar se a média aparece e o botão mudou para Resetar
    await expect(page.getByText('Média', { exact: false }).first()).toBeVisible();
    await expect(page.getByText('Resultados')).toBeVisible();

    const resetButton = page.getByRole('button', { name: 'Resetar' });
    await expect(resetButton).toBeVisible();

    // 6. Resetar a rodada
    await resetButton.click();

    // Verificar se voltou ao estado inicial (sem votos e botão Reveal disponível)
    await expect(page.getByText('Votou')).not.toBeVisible();
    await expect(page.getByRole('button', { name: 'Revelar' })).toBeVisible();
});
