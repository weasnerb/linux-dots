--  NOTE: Must happen before plugins are required (otherwise wrong leader will be used)
vim.g.mapleader = ' '
vim.g.maplocalleader = ' '

-- Open Nvim File Explorer
vim.keymap.set("n", "<leader>fe", vim.cmd.Ex)

-- Keep highlighted values when changing indentation
vim.keymap.set("v", "<", "<gv")
vim.keymap.set("v", ">", ">gv")

-- Move highlighted lines up or down
vim.keymap.set("v", "J", ":m '>+1<CR>gv=gv")
vim.keymap.set("v", "K", ":m '<-2<CR>gv=gv")

-- Keep cursor in current position when appending the line below to current line
vim.keymap.set("n", "J", "mzJ`z")

-- Keep cursor in center of screen when doing half page jumps
vim.keymap.set("n", "<C-d>", "<C-d>zz")
vim.keymap.set("n", "<C-u>", "<C-u>zz")

-- Keep cursor in center of screen when doing search
vim.keymap.set("n", "n", "nzzzv")
vim.keymap.set("n", "N", "Nzzzv")

-- Paste, deleting highlighted content without putting deleted content into register
vim.keymap.set("x", "<leader>p", "\"_dP")

-- Yank to system clipboard
vim.keymap.set("n", "<leader>y", "\"+y")
vim.keymap.set("v", "<leader>y", "\"+y")
-- Yank till end of line to system clipboard
vim.keymap.set("n", "<leader>Y", "\"+Y")

-- Delete to void register
vim.keymap.set("n", "<leader>d", "\"_d")
vim.keymap.set("v", "<leader>d", "\"_d")

