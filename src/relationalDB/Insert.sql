-- Inserir Cargos
INSERT INTO Cargo (Nome) VALUES 
('Atendente'),
('Padeiro'),
('Gerente');

-- Inserir Funcionários (Staff)
INSERT INTO Staff (Nome, Email, CargoID) VALUES 
('Carlos Oliveira', 'carlos@pastelaria.com', 1), -- Atendente
('Ana Sousa', 'ana@pastelaria.com', 2), -- Padeiro
('Fernanda Lima', 'fernanda@pastelaria.com', 3); -- Gerente

-- Inserir Clientes
INSERT INTO Cliente (Nome, NIF) VALUES 
('João Silva', 123456789),
('Maria Souza', 987654321);

-- Inserir Produtos
INSERT INTO Produto (Nome, Preço) VALUES 
('Pastel de Nata', 1.50),
('Croissant', 2.00),
('Bola de Berlim', 2.50);

-- Inserir Pedidos
INSERT INTO Pedido (ClienteID, StaffID, Data, Status) VALUES 
(1, 1, '2025-03-10', 'Pendente'),
(2, 1, '2025-03-11', 'Finalizado');

-- Inserir Itens nos Pedidos
INSERT INTO Pedido_Produto (PedidoID, ProdutoID, Quandidade) VALUES 
(1, 1, 2),  -- 2 Pastéis de Nata no Pedido 1
(1, 3, 1),  -- 1 Bola de Berlim no Pedido 1
(2, 2, 3);  -- 3 Croissants no Pedido 2
